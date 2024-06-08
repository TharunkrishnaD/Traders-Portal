from django.shortcuts import render,redirect,get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from requests import request
import pyrebase
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
import firebase_admin
from firebase_admin import credentials, auth
from .models import Company,WatchlistEntry
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib import messages

# Create your views here.
firebaseConfig={
    'apiKey': "AIzaSyAGVQPzA6r8OA8WBxEUkOPpZu1MX7b4aVU",
    'authDomain': "fir-6ea77.firebaseapp.com",
    'projectId': "fir-6ea77",
    'storageBucket': "fir-6ea77.appspot.com",
    'messagingSenderId': "865285818099",
    'appId': "1:865285818099:web:47b7f218ae37c03f33d986",
    'measurementId': "G-GMH9M2DV6Y",
    'databaseURL': "https://fir-6ea77-default-rtdb.firebaseio.com/"
}
# Initialising database,auth and firebase for further use 
firebase=pyrebase.initialize_app(firebaseConfig)
authe = firebase.auth()


def signIn(request):
    return render(request, "home/mains.html")

def signup(request):
    return render(request, "home/login.html")

def postsignIn(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        email = data.get('email')
        
        pasw = data.get('password')
        try:
            user = authe.sign_in_with_email_and_password(email, pasw)
            request.session['email'] = email
            request.session['uid'] = str(user['idToken'])
            return JsonResponse({'success': True})
        except Exception as e:
            error_json = e.args[1]
            error = json.loads(error_json)['error']['message']
            if error == 'EMAIL_NOT_FOUND' or error == 'INVALID_PASSWORD':
                message = "Invalid Credentials! Please check your data"
            else:
                message = "An error occurred: " + error
            return JsonResponse({'success': False, 'message': message})
    else:
        return JsonResponse({'success': False, 'message': 'Invalid request method'})
 

def list(request):
    companies_list = Company.objects.all()
    email = request.session.get('email')
    
    watchlist_entries = WatchlistEntry.objects.filter(user=email)
    company_ids = [entry.company_id for entry in watchlist_entries]

    # Handle search functionality
    search_query = request.GET.get('search', '')
    print(search_query)
    if search_query:
        companies_list = companies_list.filter(
            Q(company_name__icontains=search_query) |
            Q(symbol__icontains=search_query) |
            Q(scripcode__icontains=search_query)
        )

    paginator = Paginator(companies_list, 10)  # Show 10 companies per page

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, "home/list.html", {
        'email': email,
        'page_obj': page_obj,
        'company_ids': company_ids,
        'search_query': search_query  # Pass search query to template
    })


def add_to_watchlist(request, company_id):
    company = Company.objects.get(id=company_id)
    email = request.session.get('email')
    WatchlistEntry.objects.get_or_create(user=email, company=company)
    return redirect('watchlist')

def watchlist(request):
    email = request.session.get('email')
    
    # Fetch watchlist entries for the logged-in user
    watchlist_entries = WatchlistEntry.objects.filter(user=email)

    if request.method == 'POST':
        company_id = request.POST.get('company_id')
        # Logic to remove the company from the watchlist
        try:
            entry_to_remove = WatchlistEntry.objects.get(user=email, company_id=company_id)
            entry_to_remove.delete()
            messages.success(request, 'Company removed from watchlist successfully.')
            return redirect('watchlist')  # Redirect to refresh the page after removal
        except WatchlistEntry.DoesNotExist:
            messages.error(request, 'Company not found in watchlist.')
            return redirect('watchlist')

    return render(request, "home/watchlist.html", {
        'watchlist_entries': watchlist_entries,
    })

def remove_from_watchlist(request, company_id):
    email = request.session.get('email')
    
    # Ensure the user is authenticated and fetch the WatchlistEntry
    watchlist_entry = get_object_or_404(WatchlistEntry, user=email, company_id=company_id)

    if request.method == 'POST':
        # Delete the WatchlistEntry
        watchlist_entry.delete()
        messages.success(request, 'Company removed from watchlist successfully.')
        return redirect('watchlist')  # Redirect back to the watchlist page after removal

    # In case of a GET request or any other scenario, handle accordingly
    return redirect('watchlist')




 
def postsignUp(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        email = data.get('useremail')
        passs = data.get('userpass')
        try:
            # Creating a user with the given email and password
            user = authe.create_user_with_email_and_password(email, passs)
            uid = user['localId']
            request.session['uid'] = str(user['idToken'])
            return JsonResponse({'success': True})
        except Exception as e:
            error_json = e.args[1]
            error = json.loads(error_json)['error']['message']
            if error == 'EMAIL_EXISTS':
                message = "Email already exists"
            else:
                message = "An error occurred: " + error
            return JsonResponse({'success': False, 'message': message})
    else:
        return JsonResponse({'success': False, 'message': 'Invalid request method'})
    

# Initialize Firebase Admin SDK
cred = credentials.Certificate("fir-6ea77-firebase-adminsdk-bmmsh-98a413929d.json")
firebase_admin.initialize_app(cred)


# @csrf_exempt
# def googleSignIn(request):
#     if request.method == 'POST':
#         data = json.loads(request.body)
#         token = data.get('token')
#         email = data.get('email')
#         provider = data.get('provider')
#         displayName = data.get('displayName')

#         try:
#             decoded_token = auth.verify_id_token(token)
#             uid = decoded_token['uid']
#             # Perform additional logic here (e.g., save user data, set session)
#             request.session['uid'] = uid
#             return JsonResponse({'success': True})
#         except Exception as e:
#             return JsonResponse({'success': False, 'message': str(e)})
#     else:
#         return JsonResponse({'success': False, 'message': 'Invalid request method'})

@csrf_exempt
def firebase_login_save(request):
    username=request.POST.get("username")
    email=request.POST.get("email")
    provider=request.POST.get("provider")
    token=request.POST.get("token")
    firbase_response=loadDatafromFirebaseApi(token)
    firbase_dict=json.loads(firbase_response)
    if "users" in firbase_dict:
        user=firbase_dict["users"]
        if len(user)>0:
            user_one=user[0]
            if email==user_one["email"]:
                provider1=user_one["providerUserInfo"][0]["providerId"]
                if user_one["emailVerified"]==1 or user_one["emailVerified"]==True or user_one["emailVerified"]=="True" or provider1=="facebook.com":
                    # data=proceedToLogin(request,email,username,token,provider)
                    return HttpResponse("data")
                else:
                    return HttpResponse("Please Verify Your Email to Get Login")
            else:
                return HttpResponse("Unknown Email User")
        else:
            return HttpResponse("Invalid Request User Not Found")
    else:
        return HttpResponse("Bad Request")


def loadDatafromFirebaseApi(token):
    url = "https://identitytoolkit.googleapis.com/v1/accounts:lookup"

    payload = 'key=AIzaSyAGVQPzA6r8OA8WBxEUkOPpZu1MX7b4aVU='+token
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    response = request("POST", url, headers=headers, data=payload)

    return response.text

# def proceedToLogin(request,email,username,token,provider):
#     users=User.objects.filter(username=username).exists()

#     if users==True:
#         user_one=User.objects.get(username=username)
#         user_one.backend='django.contrib.auth.backends.ModelBackend'
#         login(request,user_one)
#         return "login_success"
#     else:
#         user=User.objects.create_user(username=username,email=email,password=settings.SECRET_KEY)
#         user_one=User.objects.get(username=username)
#         user_one.backend='django.contrib.auth.backends.ModelBackend'
#         login(request,user_one)
#         return "login_success"