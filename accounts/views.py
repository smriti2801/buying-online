from django.contrib.auth import login, authenticate, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.shortcuts import render, redirect
from django.views.generic import View, DetailView, CreateView, FormView, UpdateView

from django.utils.http import is_safe_url

from .models import EmailActivation, GuestEmail
from django.core.urlresolvers import reverse
from django.utils.safestring import mark_safe
from django.contrib import messages

from .forms import ReactivateEmailForm, LoginForm, RegisterForm, GuestForm, UserDetailChangeForm
from django.views.generic.edit import FormMixin

from ecommerce.mixins import NextUrlMixin, RequestFormAttachMixin

User = get_user_model()
# Create your views here.


class AccountHomeView(LoginRequiredMixin, DetailView):
	template_name = 'accounts/home.html'
	def get_object(self):
		return self.request.user


class UserDetailUpdateView(LoginRequiredMixin, UpdateView):
	form_class = UserDetailChangeForm
	template_name = 'accounts/update-detail-view.html'

	def get_object(self):
		return self.request.user

	def get_context_data(self, *args, **kwargs):
		context = super(UserDetailUpdateView, self).get_context_data(*args, **kwargs)
		context['title'] = 'Change Your Account Details'
		return context

	def get_success_url(self):
		return reverse("account:home")



class AccountEmailActivateView(FormMixin, View):
	success_url = '/login/'
	form_class = ReactivateEmailForm
	key=None
	def get(self, request, key=None, *args, **kwargs):
		self.key=key #bcoz we dont send any kwargs named key
		if key is not None:
			qs = EmailActivation.objects.filter(key__iexact=key)
			confirm_qs = qs.confirmable()

			if confirm_qs.count()==1:
				obj = confirm_qs.first()
				obj.activate()
				messages.success(request, "You email has been activated. You can login")
				return redirect("login")
			else:
				activated_qs = qs.filter(activated=True)
				print(activated_qs)
				if activated_qs.exists():
					reset_link = reverse("password_reset")
					msg = """Your email has already been confirmed
					Do you need to <a href="{link}">reset your password</a>?
					""".format(link=reset_link)

					messages.success(request, mark_safe(msg))
					return redirect("login")
		context = {'form': self.get_form(), 'key':key}
		return render(request, 'registration/activation-error.html', context)

	def post(self, request, *args, **kwargs):
		# create form to receive an email
		form = self.get_form()
		if form.is_valid():
			return self.form_valid(form)
		else:
			return self.form_invalid(form)

	def form_valid(self, form):
		msg = """Activation link sent, please check your email"""
		request = self.request
		messages.success(request, msg)
		email = form.cleaned_data.get("email")
		obj = EmailActivation.objects.email_exists(email).first()
		user = obj.user
		new_activation = EmailActivation.objects.create(user=user, email=email)
		new_activation.send_activation_email()
		return super(AccountEmailActivateView, self).form_valid(form)

	def form_invalid(self, form):
		context = {'form': form, 'key':self.key}
		return render(self.request, 'registration/activation-error.html', context)



def home_page(request):
	return render( request, 'base.html', {} )



class GuestRegisterView(NextUrlMixin, RequestFormAttachMixin, CreateView):
	form_class=GuestForm
	default_url ="/register/"

	def get_success_url(self):
		return self.get_next_url()

	def form_invalid(self, form):
		return redirect(self.default_url)


class LoginView(NextUrlMixin, RequestFormAttachMixin, FormView):
	form_class=LoginForm
	#success_url=self.get_next_url()
	template_name='accounts/login.html'
	#default_url ="/"

	def form_valid(self, form):
		next_path = self.get_next_url()
		return redirect(next_path)


class RegisterView(CreateView):
	form_class=RegisterForm
	template_name='accounts/login.html'
	success_url='/login/'

	# def guest_register_page(request):
# 	form_class=GuestForm(request.POST or None)
# 	#print(form_class)
# 	context={"form":form_class}

# 	next_ = request.GET.get('next')
# 	next_post = request.POST.get('next')
# 	redirect_path = next_ or next_post or None
# 	print(redirect_path)

# 	if form_class.is_valid():
# 		if is_safe_url(redirect_path, request.get_host()):
# 			email = form_class.cleaned_data.get('email')
# 			emailid = GuestEmail.objects.create(email=email)
# 			request.session['guest_email_id'] = emailid.id
# 			return redirect(redirect_path)
# 		else:
# 			return redirect('/register/')
# 	else:
# 		print("Error")
# 	return redirect('/register/')


	# def form_valid(self, form):
	# 	request=self.request
	# 	next_ = request.GET.get('next')
	# 	next_post = request.POST.get('next')
	# 	redirect_path = next_ or next_post or None

	# 	username = form.cleaned_data.get('username')
	# 	password = form.cleaned_data.get('password')
	# 	user = authenticate(request, username=username, password=password)

	# 	if user:
	# 		if not user.is_active:
	# 			messages.error(request, "This user is inactive")
	# 			return super(LoginView, self).form_invalid(form)

	# 		login(request,user)
	# 		try:
	# 			del request.session['guest_email_id']
	# 		except:
	# 			pass

	# 		if is_safe_url(redirect_path, request.get_host()):
	# 			return redirect(redirect_path)
	# 		else:
	# 			return redirect('/')
	# 	else:
	# 		print("Error")
	# 	return super(LoginView, self).form_invalid(form)



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