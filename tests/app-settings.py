# --------------------------------------------------------------------
# Tests: app-settings.py
#
# Testings settings value from Yaml or JSon files
# --------------------------------------------------------------------

# libs
import sys
import mblibs
from mblibs import testing_successed, testing_failed, testing_function
from mblibs.fast import FastSettings
from pprint import pprint


# --------------------------------------------------------------------
def main(config_pathname):
    # load configuration
    settings = FastSettings(config_pathname)

    # --------------------------------------------------------------------
    @testing_function("Integer value from settings")
    def check_int():
        val = settings.getInt("/app/width_1", parent_search=True)
        if not type(val) is int:
            raise Exception("not a integer value")
    check_int()

    # --------------------------------------------------------------------
    @testing_function("check value from same settings key (array in JSON)")
    def check_arraykeys():
        val = settings.get("/app/list/test[1]", default="nop")
        if val != "value 2":
            raise Exception("not a correct value")
    check_arraykeys()

    # --------------------------------------------------------------------
    @testing_function("list values from settings")
    def check_listoutput():
        # get list
        list_graphics = settings.get("/app/output", [])
        if len(list_graphics) == 0:
            raise Exception("no testing values /app/output")
    check_listoutput()

    # --------------------------------------------------------------------
    @testing_function("Get real title from graphic_A")
    def check_righttitle():
        # check 
        if settings.get("/app/output/graphic_A/title") != "Base Graphics":
            raise Exception("./graphic_A/title failed to find right value")
    check_righttitle()

    # --------------------------------------------------------------------
    @testing_function("Get hierarchic title from graphic_B")
    def check_hierarchic1():
        # check
        if settings.get("/app/output/graphic_B/title", default="nop", parent_search=True) != "A current main title":
            raise Exception("./graphic_B/title failed to find right value")
    check_hierarchic1()

    # --------------------------------------------------------------------
    @testing_function("Get hierarchic subtitle from graphic_A")
    def check_hierarchic2():
        # check
        if settings.get("/app/output/graphic_A/subtitle", default="nop", parent_search=True) != "testing main subtitle":
            raise Exception("./graphic_B/title failed to find right value")
    check_hierarchic2()

    # resume
    print("")
    print("{} test{} successed.".format(
        testing_successed(), "s" if testing_successed() > 1 else ""))
    print("{} test{} failed.".format(
        testing_failed(), "s" if testing_failed() > 1 else ""))


# --------------------------------------------------------------------
if __name__ == '__main__':
    # get configuration file
    config_pathname = sys.argv[1] if len(sys.argv) > 1 else "./app-settings.yml"

    # démarrage du programme
    try:
        main(config_pathname)
        print("mblibs testing settings (v{})".format(mblibs.__version__))

    except Exception as e:
        print("\n\n\n** Something went wrong:\n{}".format(str(e)))
        print("\nExiting.")


