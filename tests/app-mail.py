# --------------------------------------------------------------------
# Tests: app-mail.py
#
# Testings send email
# --------------------------------------------------------------------

# libs
import sys
import mblibs
from mblibs import testing_successed, testing_failed, testing_function
from mblibs.fast import FastSettings, FastEmail
from pprint import pprint

# --------------------------------------------------------------------
def main(config_pathname):
	# load configuration
	settings = FastSettings(config_pathname)

	@testing_function("Send email with attachment and embedded image")
	def check_sendmail():
		# procédure d'envoi du courrier
		mailer = FastEmail()
		mailer.mail_from = settings.get("/smtp/mail_from")
		mailer.mail_subject = "A subject for the mail."
		mailer.mail_text = 'Merci de lire le message depuis un lecteur acceptant le HTML.'
		mailer.mail_html = open(settings.get("/smtp/mail_template"), "rb").read()
		mailer.smtp_host = settings.get("/smtp/host", "localhost")
		mailer.smtp_port = settings.getInt("/smtp/port", 25)
		mailer.smtp_tls = settings.getEnable("/smtp/tls")
		mailer.smtp_login = settings.get("/smtp/login")
		mailer.smtp_password = settings.get("/smtp/password")

		To = [settings.get("/smtp/mail_to")]
		filename = "./ridev.png"
		return mailer.send_mail(to=To, cc=[], bcc=[], attachfiles=[filename],
								embeddedimages_tag="graphic",
								embeddedimages=["./python.png", filename])

	check_sendmail()

	# resume
	print("")
	print("{} test{} successed.".format(
		testing_successed(), "s" if testing_successed() > 1 else ""))
	print("{} test{} failed.".format(
		testing_failed(), "s" if testing_failed() > 1 else ""))


# --------------------------------------------------------------------
if __name__ == '__main__':
    # get configuration file
    config_pathname = sys.argv[1] if len(
        sys.argv) > 1 else "./app-settings.yml"

    # démarrage du programme
    try:
        main(config_pathname)
        print("mblibs testing settings (v{})".format(mblibs.__version__))

    except Exception as e:
        print("\n\n\n** Something went wrong:\n{}".format(str(e)))
        print("\nExiting.")
