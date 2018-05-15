from django.contrib.auth import login, authenticate, get_user_model
from django.shortcuts import render, redirect
from django.views.generic import CreateView, FormView
from .forms import LoginForm, RegisterForm, GuestForm
from .models import GuestEmail

from django.utils.http import is_safe_url

User = get_user_model()
# Create your views here.

def home_page(request):
	return render( request, 'base.html', {} )

def guest_register_page(request):
	form_class=GuestForm(request.POST or None)
	#print(form_class)
	context={"form":form_class}

	next_ = request.GET.get('next')
	next_post = request.POST.get('next')
	redirect_path = next_ or next_post or None
	print(redirect_path)

	if form_class.is_valid():
		if is_safe_url(redirect_path, request.get_host()):
			email = form_class.cleaned_data.get('email')
			print(email)
			emailid = GuestEmail.objects.create(email=email)
			print(str(emailid))
			request.session['guest_email_id'] = emailid.id
			return redirect(redirect_path)
		else:
			return redirect('/register/')
	else:
		print("Error")
	return redirect('/register/')

class LoginView(FormView):
	form_class=LoginForm
	success_url='/'
	template_name='accounts/login.html'

	def form_valid(self, form):
		request=self.request
		next_ = request.GET.get('next')
		next_post = request.POST.get('next')
		redirect_path = next_ or next_post or None

		username = form_class.cleaned_data.get('username')
		password = form_class.cleaned_data.get('password')
		user = authenticate(request, username=username, password=password)

		if user:
			login(request,user)
			try:
				del request.session['guest_email_id']
			except:
				pass

			if is_safe_url(redirect_path, request.get_host()):
				return redirect(redirect_path)
			else:
				return redirect('/')
		else:
			print("Error")
		return super(LoginView, self).form_invalid(form)


class RegisterView(CreateView):
	form_class=RegisterForm
	template_name='accounts/login.html'
	success_url='/login/'



# def login_page(request):
# 	form_class=LoginForm(request.POST or None)
# 	#print(form_class)
# 	context={"form":form_class}

# 	next_ = request.GET.get('next')
# 	next_post = request.POST.get('next')
# 	redirect_path = next_ or next_post or None

# 	if form_class.is_valid():
# 		# print(form_class.cleaned_data)
# 		# context['form']=LoginForm()
# 		username = form_class.cleaned_data.get('username')
# 		password = form_class.cleaned_data.get('password')
# 		print(password)
# 		user = authenticate(request, username=username, password=password)
# 		print(user)
# 		print(request.user.is_authenticated())

# 		if user:
# 			login(request,user)
# 			try:
# 				del request.session['guest_email_id']
# 				print(request.session['guest_email_id'] + "guest id del?")
# 			except:
# 				pass

# 			if is_safe_url(redirect_path, request.get_host()):
# 				return redirect(redirect_path)
# 			else:
# 				return redirect('/')
# 		else:
# 			print("Error")
# 	return render( request, "accounts/login.html", context )


# def register_page(request):
# 	form=RegisterForm(request.POST or None)
# 	context={'form':form}
# 	if form.is_valid():
# 		form.save()

# 		# username 	= form.cleaned_data.get('username')
# 		# email 		= form.cleaned_data.get('email')
# 		# password 	= form.cleaned_data.get('psssword')

# 		new_user = User.objects.create(username, email, password)
# 	return render( request, 'accounts/login.html', context )