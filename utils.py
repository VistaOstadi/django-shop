import os
from dotenv import load_dotenv
from kavenegar import KavenegarAPI

load_dotenv()


def send_otp_code(phone_number, code):
    try:
        api_key = os.getenv("KAVENEGAR_API_KEY")
        if not api_key:
            print("Kavenegar API key not set")
            return False

        api = KavenegarAPI(api_key)
        params = {'sender': '2000660110', 'receptor': phone_number, 'message': f"your code is {code}"}
        response = api.sms_send(params)
        print(response)
        return True

    except Exception as e:
        print(e)
        return False


