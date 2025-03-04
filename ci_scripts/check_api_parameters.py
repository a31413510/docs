# Copyright (c) 2022 PaddlePaddle Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import argparse
import ast
import inspect
import json
import os.path as osp
import re
import sys


def add_path(path):
    if path not in sys.path:
        sys.path.insert(0, path)


this_dir = osp.dirname(__file__)
# Add docs/api to PYTHONPATH
add_path(osp.abspath(osp.join(this_dir, "..", "docs", "api")))
from extract_api_from_docs import extract_params_desc_from_rst_file

arguments = [
    # flags, dest, type, default, help
    ["--rst-files", "rst_files", str, None, "api rst files, sperated by space"],
    ["--api-info", "api_info_file", str, None, "api_info_all.json filename"],
]


def parse_args():
    """
    Parse input arguments
    """
    global arguments
    parser = argparse.ArgumentParser(description="check api parameters")
    parser.add_argument("--debug", dest="debug", action="store_true")
    for item in arguments:
        parser.add_argument(
            item[0], dest=item[1], help=item[4], type=item[2], default=item[3]
        )

    args = parser.parse_args()
    return args


def _check_params_in_description(rstfilename, paramstr):
    flag = True
    info = ""
    params_in_title = []
    if paramstr:
        fake_func = ast.parse(f"def fake_func({paramstr}): pass")
        # Iterate over all in_title parameters
        num_defaults = len(fake_func.body[0].args.defaults)
        num_args = len(fake_func.body[0].args.args)
        # args & defaults
        for i, arg in enumerate(fake_func.body[0].args.args):
            if i >= num_args - num_defaults:
                default_value = fake_func.body[0].args.defaults[
                    i - (num_args - num_defaults)
                ]
                params_in_title.append(f"{arg.arg}={default_value}")
            else:
                params_in_title.append(arg.arg)
        # posonlyargs
        for arg in fake_func.body[0].args.posonlyargs:
            params_in_title.append(arg.arg)
        # vararg(*args)
        if fake_func.body[0].args.vararg:
            params_in_title.append(fake_func.body[0].args.vararg.arg)
        # kwonlyargs & kw_defaults
        for i, arg in enumerate(fake_func.body[0].args.kwonlyargs):
            if (
                i < len(fake_func.body[0].args.kw_defaults)
                and fake_func.body[0].args.kw_defaults[i] is not None
            ):
                default_value = fake_func.body[0].args.kw_defaults[i]
                params_in_title.append(f"{arg.arg}={default_value}")
            else:
                params_in_title.append(arg.arg)
        # **kwargs
        if fake_func.body[0].args.kwarg:
            params_in_title.append(fake_func.body[0].args.kwarg.arg)

    funcdescnode = extract_params_desc_from_rst_file(rstfilename)
    if funcdescnode:
        items = funcdescnode.children[1].children[0].children
        list_pat = r"^<list_item>.*</list_item>$"
        if not re.match(list_pat, str(items[0])):
            flag = False
            info = "Something wrong with the format of params list in description, check it please."
        elif len(items) != len(params_in_title):
            flag = False
            if not items:
                info = (
                    "Params section in description is empty, check it please."
                )
            else:
                info = f"The number of params in title does not match the params in description: {len(params_in_title)} != {len(items)}."
            print(f"check failed (parammeters description): {rstfilename}")
        else:
            for i in range(len(items)):
                pname_in_title = params_in_title[i].split("=")[0].strip()
                mo = re.match(
                    r"\*{0,2}(\w+)\b.*", items[i].children[0].astext()
                )
                if mo:
                    pname_indesc = mo.group(1)
                    if pname_indesc != pname_in_title:
                        flag = False
                        info = f"the following param in title does not match the param in description: {pname_in_title} != {pname_indesc}."
                        print(
                            f"check failed (parammeters description): {rstfilename}, {pname_in_title} != {pname_indesc}"
                        )
                else:
                    flag = False
                    info = f"param name '{pname_in_title}' not matched in description line{i + 1}, check it please."
                    print(
                        f"check failed (parammeters description): {rstfilename}, param name not found in {i} paragraph."
                    )
    else:
        if params_in_title:
            info = "params section not found in description, check it please."
            print(
                f"check failed (parameters description not found): {rstfilename}, {params_in_title}."
            )
            flag = False
    return flag, info


def _check_params_in_description_with_fullargspec(rstfilename, funcname):
    flag = True
    info = ""
    funcspec = inspect.getfullargspec(eval(funcname))
    funcdescnode = extract_params_desc_from_rst_file(rstfilename)
    if funcdescnode:
        items = funcdescnode.children[1].children[0].children
        params_inspec = funcspec.args
        if len(items) != len(params_inspec):
            flag = False
            info = f"check_with_fullargspec failed (parammeters description): {rstfilename}"
            print(f"check failed (parammeters description): {rstfilename}")
        else:
            for i in range(len(items)):
                pname_in_title = params_inspec[i]
                mo = re.match(
                    r"\*{0,2}(\w+)\b.*", items[i].children[0].astext()
                )
                if mo:
                    pname_indesc = mo.group(1)
                    if pname_indesc != pname_in_title:
                        flag = False
                        info = f"the following param in title does not match the param in description: {pname_in_title} != {pname_indesc}."
                        print(
                            f"check failed (parammeters description): {rstfilename}, {pname_in_title} != {pname_indesc}"
                        )
                else:
                    flag = False
                    info = f"param name '{pname_in_title}' not matched in description line{i + 1}, check it please."
                    print(
                        f"check failed (parammeters description): {rstfilename}, param name not found in {i} paragraph."
                    )
    else:
        if funcspec.args:
            info = "params section not found in description, check it please."
            print(
                f"check failed (parameters description not found): {rstfilename}, {funcspec.args}."
            )
            flag = False
    return flag, info


def check_api_parameters(rstfiles, apiinfo):
    """check function's parameters same as its origin definition.

    TODO:
    1. All the documents of classes are skiped now. As
        (1) there ars many class methods in documents, may break the scripts.
        (2) parameters of Class should be checked with its `__init__` method.
    2. Some COMPLICATED annotations may break the scripts.
    """
    pat = re.compile(
        r"^\.\.\s+py:(method|function|class)::\s+([^\s(]+)\s*(?:\(\s*(.*)\s*\))?\s*$"
    )
    check_passed = []
    check_failed = {}
    api_notfound = {}
    for rstfile in rstfiles:
        rstfilename = osp.join("../docs", rstfile)
        print(f"checking : {rstfile}")
        with open(rstfilename, "r") as rst_fobj:
            func_found = False
            for line in rst_fobj:
                mo = pat.match(line)
                if mo:
                    func_found = True
                    functype = mo.group(1)
                    if functype not in ("function", "method"):
                        check_passed.append(rstfile)
                        continue
                    funcname = mo.group(2)
                    paramstr = mo.group(3)
                    flag = False
                    func_found_in_json = False
                    for apiobj in apiinfo.values():
                        if (
                            "all_names" in apiobj
                            and funcname in apiobj["all_names"]
                        ):
                            func_found_in_json = True
                            if "args" in apiobj:
                                if paramstr == apiobj["args"]:
                                    print(
                                        f"check func:{funcname} in {rstfilename} with {paramstr}"
                                    )
                                    flag, info = _check_params_in_description(
                                        rstfilename, paramstr
                                    )
                                else:
                                    print(
                                        f"check func:{funcname} in {rstfilename} with {paramstr}, but different with json's {apiobj['args']}"
                                    )
                                    flag, info = _check_params_in_description(
                                        rstfilename, paramstr
                                    )
                            else:  # paddle.abs class_method does not have `args` in its json item.
                                print(
                                    f"check func:{funcname} in {rstfilename} with its FullArgSpec"
                                )
                                flag, info = (
                                    _check_params_in_description_with_fullargspec(
                                        rstfilename, funcname
                                    )
                                )
                            break
                    if not func_found_in_json:  # may be inner functions
                        print(
                            f"check func:{funcname} in {rstfilename} with its FullArgSpec"
                        )
                        flag = _check_params_in_description_with_fullargspec(
                            rstfilename, funcname
                        )
                    if flag:
                        check_passed.append(rstfile)
                        print(f"check success: {rstfile}")
                    else:
                        check_failed[rstfile] = info
                        print(f"check failed: {rstfile}")
                    break
            if not func_found:
                info = 'funcname in title is not found, please check the format of ".. py:function::func()"'
                api_notfound[rstfile] = info
                print(f"check failed (object not found): {rstfile}")
            print(f"checking done: {rstfile}")
    return check_passed, check_failed, api_notfound


if __name__ == "__main__":
    args = parse_args()
    rstfiles = [fn for fn in args.rst_files.split(" ") if fn]
    apiinfo = json.load(open(args.api_info_file))
    check_passed, check_failed, api_notfound = check_api_parameters(
        rstfiles=rstfiles, apiinfo=apiinfo
    )
    result = True
    if check_failed:
        result = False
        for path, info in check_failed.items():
            print(f"Checking failed file:{path}\nError:{info}\n")
    if api_notfound:
        for path, info in api_notfound.items():
            print(f"Checking failed file:{path}\nError:{info}\n")
    if result:
        sys.exit(0)
    else:
        sys.exit(1)
