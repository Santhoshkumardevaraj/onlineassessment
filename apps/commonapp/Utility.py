import logging
import traceback
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import base64
from datetime import datetime
import json


class UtilityMaster:   

    def __init_(self):
        pass

    def ErrorLog(exception=None, error_details=None):
        """
        Logs exception info and optional additional error details.

        Args:
            exception (Exception or None): The caught exception (optional).
            error_details (dict or None): Additional context/error data (optional).
        """
        logger = logging.getLogger('django')

        log_data = "\n\n##### ERROR {} #####\n".format(datetime.now().strftime("%Y-%B-%d %H:%M:%S:%f"))

        if exception:
            log_data += "\nException Type: {}".format(type(exception))
            log_data += "\nException Message: {}".format(exception)
            log_data += "\nException Arguments: {}".format(exception.args)
            log_data += "\nException Traceback:\n{}".format(traceback.format_exc())
        
        if error_details:
            try:
                # Serialize error_details dict to pretty JSON string
                error_details_json = json.dumps(error_details, indent=4, default=str)
            except Exception as e:
                # Fallback if serialization fails
                error_details_json = str(error_details) + f"\n(Note: Failed to serialize error details: {e})"

            log_data += "\nAdditional Error Details:\n{}".format(error_details_json)

        logger.error(log_data)
    

    def encrypt(plain_text):
        key = b'ThisIsASecretKey'   # Must be 16, 24, or 32 bytes long
        iv = b'ThisIsAnIV456789'    # Must be 16 bytes long
        cipher = AES.new(key, AES.MODE_CBC, iv)
        ct_bytes = cipher.encrypt(pad(plain_text.encode('utf-8'), AES.block_size))
        return base64.b64encode(ct_bytes).decode('utf-8')

    def decrypt(cipher_text):
        #key = b'ThisIsASecretKey'   # Must be 16, 24, or 32 bytes long
        #iv = b'ThisIsAnIV456789'    # Must be 16 bytes long
        key = b'ThisIsASecretKey'   # Must be 16, 24, or 32 bytes long
        iv = b'ThisIsAnIV456789'    # Must be 16 bytes long
        cipher = AES.new(key, AES.MODE_CBC, iv)
        ct_bytes = base64.b64decode(cipher_text)
        pt = unpad(cipher.decrypt(ct_bytes), AES.block_size)
        return pt.decode('utf-8')
    
    def is_void_value(input):
        returnvalue=None
        if input is None or input=='' or input=='--select--' or input.lower()=='all':
            returnvalue=None
        else:
            returnvalue=input
        return returnvalue
    

