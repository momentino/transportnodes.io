from django import forms
from django.core.mail import send_mail
class ContactForm(forms.Form):
    subject=forms.CharField(max_length=100)
    name = forms.CharField(max_length=100)
    email = forms.EmailField(max_length=100)
    message = forms.CharField(widget=forms.Textarea(attrs={"rows":10, "cols":10}))

    def send_email(self):
        # send email using the self.cleaned_data dictionary
        subject = self.cleaned_data['subject']
        message = self.cleaned_data['message']
        email = self.cleaned_data['email']
        name = self.cleaned_data['name']
        recipients = []

        # Send email to filippomomente@gmail.com
        send_mail(subject, message, email, recipients)
        # Send to the user successful sending confirm
        receiver = [email]
        sender = ""
        send_mail("Transportnodes.io - Confirmation Email Sent", "Your email has been sent! We will get in touch with you soon.", sender, receiver)
        print(message)
        #return HttpResponseRedirect('/thanks/')

   