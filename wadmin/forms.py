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
from util.tools import getCachedAccessWechatObj
from weixin.models import *

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


class WeiXinPublicAccountForm(forms.ModelForm):
    def __init__(self, request=None, *args, **kwargs):
        self.request = request
        super(WeiXinPublicAccountForm, self).__init__(*args, **kwargs)

    id = forms.CharField(widget=forms.HiddenInput, required=False)


    class Meta:
        model = WeiXinPublicAccount
        fields = ['id', 'name', 'type', 'appID', 'appSecret']

    def clean(self):
        appID = self.cleaned_data["appID"]
        appSecret = self.cleaned_data["appSecret"]
        if appID and appSecret:
            if not getCachedAccessWechatObj(appID, appSecret):
                raise forms.ValidationError('appID或appSecret错误')
        return super(WeiXinPublicAccountForm, self).clean()

    def save(self, commit=True):
        obj = super(WeiXinPublicAccountForm, self).save(commit=False)
        obj.user = self.request.user
        if not obj.token:
            obj.token = str(uuid.uuid1()).replace('-', '').upper()
        if not obj.appID:
            obj.appID = None
        if not obj.appSecret:
            obj.appSecret = None
        if commit:
            obj.save()
        return obj


class SubjectForm(forms.ModelForm):
    start_time = forms.DateTimeField(widget=SplitDateTimeWidget, label=u'开始时间')
    end_time = forms.DateTimeField(widget=SplitDateTimeWidget, label=u'结束时间')


    def __init__(self, request=None, *args, **kwargs):
        self.request = request
        super(SubjectForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Subject
        fields = ['account', 'name', 'start_time', 'end_time', 'is_check', 'status', 'background', 'logo']

    def clean_account(self):
        account = self.cleaned_data["account"]
        if not account.user == self.request.user:
            raise forms.ValidationError(u'非法数据')
        return account

    def save(self, commit=True):
        obj = super(SubjectForm, self).save(commit=False)
        if not obj.user_id:
            obj.user_id = self.request.user.pk
        if not obj.url_ticket:
            obj.url_ticket = str(uuid.uuid1()).replace('-', '').upper()
        if commit:
            obj.save()
        return obj


class ProgrammeForm(forms.ModelForm):
    def __init__(self, request=None, *args, **kwargs):
        self.request = request
        super(ProgrammeForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Programme
        fields = ['name', 'subject', 'template']

    def clean_subject(self):
        subject = self.cleaned_data["subject"]
        if not subject.user_id == self.request.user.pk:
            raise forms.ValidationError(u'非法数据')
        return subject

    def save(self, commit=True):
        obj = super(ProgrammeForm, self).save(commit=False)
        subject = obj.subject
        account = subject.account
        if obj.user_id == None:
            obj.user_id = self.request.user.pk
        if obj.account_id != account.pk:
            obj.account_id = account.pk
            obj.scene_id = None
            obj.ticket = None
            obj.index = None

        if obj.scene_id == None:
            pros = Programme.objects.filter(account_id=account.pk).order_by('-scene_id')[:1]
            scene_id = 1
            if pros.count() > 0:
                scene_id = pros[0].scene_id + 1
            obj.scene_id = scene_id
        if obj.ticket == None:
            if account.appID and account.appSecret:
                wechat = getCachedAccessWechatObj(account.appID, account.appSecret)
                if wechat:
                    try:
                        res = wechat.create_qrcode(action_name="QR_LIMIT_SCENE",
                                                   action_info={"scene": {"scene_id": obj.scene_id}})
                        obj.ticket = res.get('ticket', None)
                    except:
                        pass
        if obj.index == None:
            index = 1
            pros = Programme.objects.filter(subject=subject).order_by('-index')[:1]
            if pros.count() > 0:
                index = pros[0].index + 1
            obj.index = index

        if commit:
            obj.save()
            if obj.template.type.value == 'vote' and (not hasattr(obj, 'vote') or obj.vote == None):
                Vote.objects.create(user_id=self.request.user.pk, programme=obj)

        return obj


class VoteItemForm(forms.ModelForm):
    def __init__(self, request=None, *args, **kwargs):
        self.request = request
        super(VoteItemForm, self).__init__(*args, **kwargs)

    class Meta:
        model = VoteItem
        fields = ['title', 'required', 'max_select', 'vote']

    def save(self, commit=True):
        obj = super(VoteItemForm, self).save(commit=False)
        vote = obj.vote
        if not obj.user_id:
            obj.user_id = self.request.user.pk
        if obj.index == None:
            index = 1
            pros = VoteItem.objects.filter(vote=vote).order_by('-index')[:1]
            if pros.count() > 0:
                index = pros[0].index + 1
            obj.index = index
        if commit:
            obj.save()
        return obj