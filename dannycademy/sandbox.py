def run(code):
    import epicbox

    epicbox.configure(
        profiles=[
            epicbox.Profile('python', 'python:3.6.5-alpine')
        ]
    )
    files = [{'name': 'main.py', 'content': code}]
    limits = {'cputime': 1, 'memory': 64, 'timelimit':1, 'realtime':1}
    result = epicbox.run('python', 'python3 main.py', files=files, limits=limits)
    print("limits: ")
    print(result)


    print()
    print()
    print()
    print("the error was:")
    print(result["stderr"].decode("utf-8"))
    print("the output was:")
    print(result["stdout"].decode("utf-8"))
    return result
