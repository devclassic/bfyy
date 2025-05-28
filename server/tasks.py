from invoke import task


@task
def build(c):
    c.run("pyinstaller -F --collect-all tortoise main.py")
