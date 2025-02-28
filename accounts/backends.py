from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

class AccountBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        UserModel = get_user_model()
        
        # Try to authenticate using email
        try:
            user = UserModel.objects.get(email=username)
        except UserModel.DoesNotExist:
            # If not found, try to authenticate using account_id
            try:
                user = UserModel.objects.get(account_id=username)
            except UserModel.DoesNotExist:
                return None
        
        # Check the password
        if user.check_password(password):
            return user
        return None