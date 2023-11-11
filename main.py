import os
import random

import click
import libtmux
import tqdm

PORT = 2222


def connect_to_session(session_name: str):
    server = libtmux.Server()
    if not server.has_session(target_session=session_name):
        raise RuntimeWarning(f"There is no tmux-session with name {session_name}")
    session = server.sessions.get(session_name=session_name)
    return session


@click.group()
def cli():
    pass


@click.command()
@click.argument("num_users", type=click.INT)
@click.option("--base-dir", default="./", help="рабочая директория")
@click.option("--session-name", default="jupyter", help="название сессии")
def start(num_users: int, base_dir='./', session_name="jupyter") -> None:
    """
    Запустить $num_users ноутбуков. У каждого рабочая директория $base_dir+$folder_num
    """
    if num_users <= 0:
        # raise ValueError("Number of notebooks is positive.")
        print("Number of notebooks is positive.")
        return
    base_dir = base_dir + "/" if base_dir[-1] != '/' else base_dir
    if not os.path.exists(base_dir):
        # raise ValueError("No such base directory. ")
        print("No such base directory. ")
        return
    server = libtmux.Server()
    if server.has_session(target_session=session_name):
        # raise RuntimeWarning("The session with jupyter notebooks is already running, the notebooks are deployed.")
        print("The session with jupyter notebooks is already running, the notebooks are deployed.")
        return
    session = None
    for i in tqdm.trange(num_users):
        if not os.path.exists(f"{base_dir}dir{i}"):
            os.makedirs(f"{base_dir}dir{i}")
        token = random.getrandbits(128)
        jupyter_run_command = f"jupyter notebook --allow-root --port {PORT + i} --no-browser --NotebookApp.token={token} --NotebookApp.notebook_dir={base_dir}dir{i}"
        if i == 0:
            server.new_session(session_name=session_name,
                               start_directory=f"{base_dir}dir{i}").attached_pane.send_keys(cmd=jupyter_run_command)
            session = server.sessions.get(session_name=session_name)
        else:
            session.new_window(attach=False,
                               start_directory=f"{base_dir}dir{i}").attached_pane.send_keys(cmd=jupyter_run_command)
        click.echo(f"jupyter notebook number {i}: port {PORT + i}, token {token}")


@click.command()
@click.argument("num", type=click.INT)
@click.option("--session-name", default="jupyter", help="Названия tmux-сессии, в которой запущены окружения",
              type=click.STRING)
def stop(session_name: str, num: int) -> None:
    """
    @:param session_name: Названия tmux-сессии, в которой запущены окружения
    @:param num: номер ноутбука, кот. можно убить
    """
    try:
        session = connect_to_session(session_name)
        session.kill_window(f"{num}")
    except RuntimeWarning as ex:
        print(ex)
    except libtmux.exc.LibTmuxException as ex:
        print(ex)


@click.command(name="stop_all")
@click.option("--session-name", default="jupyter", help="Названия tmux-сессии, в которой запущены окружения",
              type=click.STRING)
def stop_all(session_name: str) -> None:
    """
    @:param session_name: Названия tmux-сессии, в которой запущены окружения
    """
    try:
        session = connect_to_session(session_name)
        session.kill_session()
    except RuntimeWarning as ex:
        print(ex)


if __name__ == '__main__':
    cli.add_command(start)
    cli.add_command(stop)
    cli.add_command(stop_all)
    cli()
