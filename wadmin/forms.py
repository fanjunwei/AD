# coding=utf-8
# Date: 14/11/21
# Time: 17:21
# Email:fanjunwei003@163.com
import uuid
from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from django.forms import SplitDateTimeWidget
from wadmin.models import Article


__author__ = u'范俊伟'


class LoginForm(AuthenticationForm):
    img_code = forms.CharField(label='验证码')

    def clean_img_code(self):
        img_code = self.cleaned_data.get('img_code')
        if img_code != self.request.session['login_img_code']:
            self.request.session['login_img_code'] = None
            raise forms.ValidationError('验证码错误')
        self.request.session['login_img_code'] = None
        return img_code

    def clean(self):
        if not self.errors:
            super(LoginForm, self).clean()
        else:
            return self.cleaned_data


class RegisterForm(forms.ModelForm):
    def __init__(self, request=None, *args, **kwargs):
        self.request = request
        super(RegisterForm, self).__init__(*args, **kwargs)

    error_messages = {
        'duplicate_username': "用户已存在",
        'password_mismatch': "两次输入的密码不同",
    }
    username = forms.RegexField(label="用户名", max_length=30,
                                regex=r'^[\w.@+-]+$',
                                help_text="用户名只允许为字母、数字和字符 @/./+/-/_ 。",
                                error_messages={
                                    'invalid': "用户名只允许为字母、数字、下划线"})
    password1 = forms.CharField(label="密码",
                                widget=forms.PasswordInput)
    password2 = forms.CharField(label="确认密码",
                                widget=forms.PasswordInput,
    )

    email = forms.EmailField(label='Email')

    img_code = forms.CharField(label='验证码')

    class Meta:
        model = User
        fields = ("username",)


    def clean_username(self):
        # Since User.username is unique, this check is redundant,
        # but it sets a nicer error message than the ORM. See #13147.
        username = self.cleaned_data["username"]
        try:
            User.objects.get(username=username)
        except User.DoesNotExist:
            return username
        raise forms.ValidationError(
            self.error_messages['duplicate_username'],
            code='duplicate_username',
        )


    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(
                self.error_messages['password_mismatch'],
                code='password_mismatch',
            )
        return password2

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if self.Meta.model.objects.filter(email=email).exists():
            raise forms.ValidationError(u'Email已存在,请输入其他地址')
        return email

    def clean_img_code(self):
        img_code = self.cleaned_data.get('img_code')
        if img_code != self.request.session['login_img_code']:
            self.request.session['login_img_code'] = None
            raise forms.ValidationError('验证码错误')
        self.request.session['login_img_code'] = None
        return img_code

    def save(self, commit=True):
        user = super(RegisterForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user


class ChangePasswordForm(forms.Form):
    error_messages = {
        'password_mismatch': "两次输入的密码不同",
    }

    def __init__(self, request=None, *args, **kwargs):
        self.request = request
        super(ChangePasswordForm, self).__init__(*args, **kwargs)

    password_old = forms.CharField(label="原始密码",
                                   widget=forms.PasswordInput)
    password_new1 = forms.CharField(label="新密码",
                                    widget=forms.PasswordInput)
    password_new2 = forms.CharField(label="确认新密码",
                                    widget=forms.PasswordInput)


    def clean_password_new2(self):
        password_new1 = self.cleaned_data.get("password_new1")
        password_new2 = self.cleaned_data.get("password_new2")
        if password_new1 and password_new2 and password_new1 != password_new2:
            raise forms.ValidationError(
                self.error_messages['password_mismatch'],
                code='password_mismatch',
            )
        return password_new2


    def clean_password_old(self):
        password_old = self.cleaned_data.get("password_old")
        if not self.request.user.check_password(password_old):
            raise forms.ValidationError(u'原始密码错误')
        return password_old


    def save(self, commit=True):
        user = self.request.user
        user.set_password(self.cleaned_data["password_new1"])
        if commit:
            user.save()
        return user


class ArticleForm(forms.ModelForm):
    def __init__(self, request=None, *args, **kwargs):
        self.request = request
        super(ArticleForm, self).__init__(*args, **kwargs)


    class Meta:
        model = Article
        fields = ['title', 'content']

    def save(self, commit=True):
        object = super(ArticleForm, self).save(commit=False)
        object.user = self.request.user
        object.save()