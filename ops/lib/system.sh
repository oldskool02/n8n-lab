#!/usr/bin/env bash
check_system()
{
    check_program "Git" git
    check_program "Python" python3
    check_program "jq" jq

}