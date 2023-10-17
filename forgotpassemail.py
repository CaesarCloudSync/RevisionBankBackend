
def forgotpasswordemail(email,access_token):
    emailtext = f"""
    <h1 style="color:#264BE4;">RevisionBank</h1>
    <strong>
    Reset Password
    </strong>
    <p >
    Hello {email}
    </p>
    <p>
        A request has been received to change the password for your RevisionBank account.
    </p>
    <a style="cursor:pointer;" href="https://revisionbank.org/resetpassword?token={access_token}" target="_blank" rel="noopener noreferrer">
    <button style="width:40%;background-color: #264BE4;border: 1px solid #264BE4;border-radius: 10px;">
        <p style="color:white">Reset Password</p>
    </button>
    </a>
    """
    return emailtext
