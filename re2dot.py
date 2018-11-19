#! /usr/bin/env python3

# Copyright 2018-2888 hidva.com
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
import regexp
import rpn


def main():
    parser = argparse.ArgumentParser(description='根据正则表达式生成其对应 DFA 的状态转移图')
    parser.add_argument("regexp", help="正则表达式")
    parser.add_argument("-N", "--nfa", help="若指定, 则输出原始 NFA 对应的状态转移图. 默认值",
                        action="store_true", default=True)
    parser.add_argument("-D", "--dfa", help="若指定, 则输出原始 NFA 转换为 DFA 对应的状态转移图.", action="store_true")
    parser.add_argument("-d", "--minidfa", help="若指定, 则输出原始 NFA 转换为 DFA 并最小化后对应的状态转移图.",
                        action="store_true")
    args = parser.parse_args()

    fa = regexp.execute_rpn(rpn.convert2rpn(regexp.Lexer(args.regexp)))
    print(fa.to_dotsource())
    return


if __name__ == "__main__":
    main()
