---
title: "Unit testing with the mock module in python"
date: 2023-10-20
lastmod: 2025-01-15
url: /mocking-with-python/
author: "Flavio Hafner"
description: " "
tags: ["python", "unit-testing"]
summary: "Describes my experience from using the `mock` module with `pytest` for mocking calls to external functions."
showToc: true 
disableAnchoredHeadings: false

---

## Motivation 

Sometimes we need to test code, but we cannot run it from anywhere -- for instance, a call to the `subprocess` module invoking `sudo` won't run on a Github CI instance --, or not too often -- for instance, a call to a web API with query limits. In this case, the `mock` module from `unittest` can be used to imitate these calls and verify they are used by our code as intended. 

In this post, I summarise some of my lessons learned from developing the [`sirup`](https://github.com/ivory-tower-private-power/sirup) package, which relies on system calls to `OpenVPN`. I only cover a few technical aspects; see some resources at the end of the post.




```python
%xmode Minimal
```

    Exception reporting mode: Minimal


```python
from unittest import mock 
import subprocess

```

## Simple example



```python
output = subprocess.run(["ls", "-lh"])
vars(output)
```

    total 52K
    -rw-rw-r-- 1 flavio flavio  21 jan 12 14:51 requirements.txt
    -rw-rw-r-- 1 flavio flavio 18K jan 12 15:31 tutorial-mocking.ipynb
    -rw-rw-r-- 1 flavio flavio 25K jan 12 14:19 tutorial-mocking.md





    {'args': ['ls', '-lh'], 'returncode': 0, 'stdout': None, 'stderr': None}




```python
def list_files(path, pwd):
    "Use sudo to list files in `path`."
    cmd = ["sudo", "-S", "ls", "-lh", path]
    output = subprocess.run(cmd, input=pwd.encode())
    return output

@mock.patch("subprocess.run") #the decorators are passed as first arguments to the function
def test_list_files(mock_subprocess_run, fail=False):
    if not fail:
        output = list_files("mypath", "my_password")
    mock_subprocess_run.assert_called_once()
```


```python
test_list_files()
```


```python
test_list_files(fail=True)
```


    AssertionError: Expected 'run' to have been called once. Called 0 times.



Instead of `assert_called_once()`, we can use `assert_called_once_with` to check precisely which arguments were used to call the function


```python
def list_files(path, pwd):
    "Use sudo to list files in `path`."
    cmd = ["sudo", "-S", "ls", "-lh", path]
    output = subprocess.run(cmd, input=pwd.encode())
    return output

@mock.patch("subprocess.run")
def test_list_files(mock_subprocess_run, fail=False):
    output = list_files("mypath", "my_password")
    cmd_expected =  ["sudo", "-S", "ls", "-lh"]
    if fail:
        cmd_expected += ["anotherpath"]
    else:
        cmd_expected += ["mypath"]
    mock_subprocess_run.assert_called_once_with(cmd_expected, input="my_password".encode())
```


```python
test_list_files()
```


```python
test_list_files(fail=True)
```


    AssertionError: expected call not found.
    Expected: run(['sudo', '-S', 'ls', '-lh', 'anotherpath'], input=b'my_password')
    Actual: run(['sudo', '-S', 'ls', '-lh', 'mypath'], input=b'my_password')



### What does the mock do?

First, we patch the `subprocess.run` function and it is passed to the test function. The test function operates on that patch instead of actually calling `subprocess.run`. Note that there are other ways to *patch*. But, the patched object records the calls made to the function, and this is the key functionality of mocking because we can assert that it was called as intended.


## Pitfall: being ambiguous 

It can be dangerous if the assertions are not specific enough, as this example illustrates:


```python
def list_files(path, pwd):
    "Use sudo to list files in `path`."
    cmd = ["sudo", "-S", "ls", "-lh", path]
    output = subprocess.run(cmd, input=pwd.encode())
    return output

@mock.patch("subprocess.run")
def test_list_files(mock_subprocess_run, fail=False):
    output = list_files("anotherpath", "my_password")
    cmd_expected = ["sudo", "-S", "ls", "-lh", "mypath"]
    if fail:
        mock_subprocess_run.assert_called_once_with(cmd_expected)
    else:
        mock_subprocess_run.assert_called_once()
```


```python
test_list_files(fail=True)
```


    AssertionError: expected call not found.
    Expected: run(['sudo', '-S', 'ls', '-lh', 'mypath'])
    Actual: run(['sudo', '-S', 'ls', '-lh', 'anotherpath'], input=b'my_password')




```python
test_list_files(fail=False)
```

The test does not fail, even though the command was not executed exactly the way we expected. I think most of the times, it is better to directly test for the exact arguments used in the call.


## Setting return values

Suppose we have a function that asks the user for the password with the `getpass` module. Instead of actually asking for a password each time we call the test function, we can set a return value to the `getpass.getpass` function, which is then further used


```python
import getpass 
```


```python
def ask_for_pw_and_list_files(path):
    "Use sudo to list files in `path`." # this function does not work in a noteobook I think
    pwd = getpass.getpass("Enter your sudo password:")
    cmd = ["sudo", "-S", "ls", "-lh", path]
    output = subprocess.run(cmd, input=pwd.encode(), stdout=subprocess.PIPE)
    return output

@mock.patch("subprocess.run")
@mock.patch("getpass.getpass")
def test_ask_for_pw_and_list_files(mock_getpass, mock_subprocess_run, fail=False): # note the order of the inputs
    if not fail:
        mock_getpass.return_value = "my_password"
    cmd_expected = ["sudo", "-S", "ls", "-lh", "mypath"]
    ask_for_pw_and_list_files("mypath")

    mock_getpass.assert_called_once()
    mock_subprocess_run.assert_called_once_with(cmd_expected, input="my_password".encode(), stdout=subprocess.PIPE)

```


```python
test_ask_for_pw_and_list_files()
```

The next one fails because the `getpass` mock is used to `ask_for_pw_and_list_files`, but no return value is set, and so `pwd` is not a string but the `mock` object itself.


```python
test_ask_for_pw_and_list_files(fail=True) 
```


    AssertionError: expected call not found.
    Expected: run(['sudo', '-S', 'ls', '-lh', 'mypath'], input=b'my_password', stdout=-1)
    Actual: run(['sudo', '-S', 'ls', '-lh', 'mypath'], input=<MagicMock name='getpass().encode()' id='139928887543632'>, stdout=-1)



## Context managers/class methods

When patching context managers, we need to patch both the `__enter__` method and the return code of the context manager. We can access class methods by using `class.return_value.method`.


```python
from subprocess import PIPE 
```


```python
def list_files_with_context(pwd, path):
    "Use sudo to list files in `path`."
    cmd = ["sudo", "-S", "ls", "-lh", path]
    with subprocess.Popen(cmd, stdin=PIPE, stdout=PIPE, stderr=PIPE) as proc:
        stdout, _ = proc.communicate(pwd.encode()) 

    return stdout 

@mock.patch("subprocess.Popen")
def test_list_files_with_context(mock_popen, type_context_mock):
    cmd_expected = ["sudo", "-S", "ls", "-lh", "."]

    # Note the two different ways of how we set the return value of `Popen`:
    if type_context_mock == "return_enter_return":
        process = mock_popen.return_value.__enter__.return_value
    elif type_context_mock == "enter_return":
        process = mock_popen.__enter__.return_value

    print(type(process))
    print(vars(process))
    print(dir(process))
    print(f"new parent: {process._mock_new_parent}")
    
    # we need to set more things
    process.communicate.return_value = (b"blah", b"")
    # process.poll.return_value = None # this silences the CalledProcessError that shows up otherwise

    # now we can call our function
    out = list_files_with_context("my_password", ".")

    mock_popen.assert_called_once_with(cmd_expected, stdin=PIPE, stdout=PIPE, stderr=PIPE)
    process.communicate.assert_called_once_with("my_password".encode())
    assert out == b"blah"

```


```python
test_list_files_with_context(type_context_mock="enter_return")
```

    <class 'unittest.mock.MagicMock'>
    {'_mock_return_value': sentinel.DEFAULT, '_mock_parent': None, '_mock_name': None, '_mock_new_name': '()', '_mock_new_parent': <MagicMock name='Popen.__enter__' id='139928887920976'>, '_mock_sealed': False, '_spec_class': None, '_spec_set': None, '_spec_signature': None, '_mock_methods': None, '_spec_asyncs': [], '_mock_children': {}, '_mock_wraps': None, '_mock_delegate': None, '_mock_called': False, '_mock_call_args': None, '_mock_call_count': 0, '_mock_call_args_list': [], '_mock_mock_calls': [], 'method_calls': [], '_mock_unsafe': False, '_mock_side_effect': None}
    ['assert_any_call', 'assert_called', 'assert_called_once', 'assert_called_once_with', 'assert_called_with', 'assert_has_calls', 'assert_not_called', 'attach_mock', 'call_args', 'call_args_list', 'call_count', 'called', 'configure_mock', 'method_calls', 'mock_add_spec', 'mock_calls', 'reset_mock', 'return_value', 'side_effect']
    new parent: <MagicMock name='Popen.__enter__' id='139928887920976'>



    ValueError: not enough values to unpack (expected 2, got 0)




```python
test_list_files_with_context(type_context_mock="return_enter_return")
```

    <class 'unittest.mock.MagicMock'>
    {'_mock_return_value': sentinel.DEFAULT, '_mock_parent': None, '_mock_name': None, '_mock_new_name': '()', '_mock_new_parent': <MagicMock name='Popen().__enter__' id='139929231216720'>, '_mock_sealed': False, '_spec_class': None, '_spec_set': None, '_spec_signature': None, '_mock_methods': None, '_spec_asyncs': [], '_mock_children': {}, '_mock_wraps': None, '_mock_delegate': None, '_mock_called': False, '_mock_call_args': None, '_mock_call_count': 0, '_mock_call_args_list': [], '_mock_mock_calls': [], 'method_calls': [], '_mock_unsafe': False, '_mock_side_effect': None}
    ['assert_any_call', 'assert_called', 'assert_called_once', 'assert_called_once_with', 'assert_called_with', 'assert_has_calls', 'assert_not_called', 'attach_mock', 'call_args', 'call_args_list', 'call_count', 'called', 'configure_mock', 'method_calls', 'mock_add_spec', 'mock_calls', 'reset_mock', 'return_value', 'side_effect']
    new parent: <MagicMock name='Popen().__enter__' id='139929231216720'>



## Conclusion

The `mock` module is helpful when we cannot call a function directly in a test. It's important to consider alternatives to mocking and patching, and if we use them, be careful about how we use them. 

## Resources
- A good video on when and how to (not) use mocking more generally, and possible alternatives, is [this PyCon talk by Edwin Jung](https://www.youtube.com/watch?v=Ldlz4V-UCFw). 
- [This blog post by Ned Batchelder](https://nedbatchelder.com/blog/202202/why_your_mock_still_doesnt_work.html) discusses the `autospec` option and has further links.

--- 


