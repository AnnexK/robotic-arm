from __future__ import annotations

import tkinter as tk
import tkinter.filedialog as filed
import tkinter.messagebox as mbox

import abc

from typing import Any, List, TextIO
from weakref import WeakSet

import roboticarm.env as env
from roboticarm.env.environment import Environment
from roboticarm.env.robot import RobotStateError
from roboticarm.env import TaskData


from roboticarm.planner.planner import Plan


class SeqViewerError(Exception):
    pass


class View(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def update_view(self, sub: SequenceViewer):
        pass


class SequenceViewer:
    def __init__(self, fallback: bool):
        self.fps: int = 30
        self.seq: Plan = []
        self.seq_iter: int = 0
        self.env: Environment = env.Environment(True, fallback)
        self.obs: WeakSet[View] = WeakSet()

    def _make_seq(self, fp: TextIO) -> Plan:
        def make_state(seq_str: str):
            if self.env.robot is not None:
                s = self.env.robot.state
                try:
                    res = tuple(float(q) for q in seq_str.split(","))
                except ValueError as exc:
                    raise SeqViewerError("Could not read sequence from file!") from exc
                try:
                    self.env.robot.state = res
                    self.env.robot.state = s
                    return tuple(float(q) for q in seq_str.split(","))
                except RobotStateError:
                    raise SeqViewerError(f"State {res} is not valid for robot!")
            return ()

        S: List[str] = fp.readlines()
        try:
            return list(make_state(q) for q in S)
        except SeqViewerError:
            raise

    def _set_new_state(self, i: int):
        if self.env.robot is None:
            raise SeqViewerError("Task not loaded!")
        if not self.seq:
            raise SeqViewerError("Sequence not loaded!")
        self.seq_iter = max(0, min(i, len(self.seq) - 1))
        self.env.robot.state = self.seq[self.seq_iter]
        self.notify()

    def next_state(self):
        self._set_new_state(self.seq_iter + 1)

    def prev_state(self):
        self._set_new_state(self.seq_iter - 1)

    def first_state(self):
        self._set_new_state(0)

    def last_state(self):
        self._set_new_state(len(self.seq) - 1)

    def current_state(self):
        return self.seq[self.seq_iter]

    def load_task(self, fp: TextIO):
        self.env.load_task(TaskData.parse_raw(fp.read()))
        self._unload_seq()

    def load_seq(self, fp: TextIO):
        if self.env.robot is None:
            raise SeqViewerError("Task not loaded!")
        self.seq = self._make_seq(fp)
        self.first_state()

    def _unload_seq(self):
        if self.env.robot:
            self.seq = [self.env.robot.state]

    def set_fps(self, fps: int):
        if fps > 0:
            self.fps = fps

    def attach(self, o: View):
        self.obs.add(o)

    def detach(self, o: View):
        self.obs.discard(o)

    def notify(self):
        for o in self.obs:
            o.update_view(self)


class SeqViewerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.viewer = SequenceViewer(False)
        self.title("Sequence Viewer")
        self.geometry("600x120")
        self._make_widgets()

    def _make_widgets(self):
        self.controls = SeqViewerControl(self.viewer, self)
        self.open = SeqViewerOpen(self.viewer, self)
        self.state = SeqViewerStateFrame(self.viewer, self)
        self.open.pack()
        self.controls.pack()
        self.state.pack()

    def report_callback_exception(self, exc, val, tb):  # type: ignore
        mbox.showerror("Error", val)  # type: ignore


class SeqViewerOpen(tk.Frame):
    def __init__(self, viewer: SequenceViewer, master: Any = None):
        super().__init__(master)
        self.master = master
        self.viewer = viewer
        self._make_widgets()

    def _make_widgets(self):
        self.b_opentask = tk.Button(self)
        self.b_opentask.config(text="Open Task", command=self.load_task)
        self.b_opentask.pack(side="right")
        self.b_openseq = tk.Button(self)
        self.b_openseq.config(text="Open Seq", command=self.load_seq)
        self.b_openseq.pack(side="right")

    def load_task(self):
        fp: TextIO = filed.askopenfile("r", filetypes=[("Task", ".json")])  # type: ignore
        try:
            if fp is not None:
                self.viewer.load_task(fp)
        finally:
            if fp is not None:
                fp.close()

    def load_seq(self):
        fp: TextIO = filed.askopenfile("r")  # type: ignore
        try:
            if fp is not None:
                self.viewer.load_seq(fp)
        finally:
            if fp is not None:
                fp.close()


class SeqViewerControl(tk.Frame):
    def __init__(self, viewer: SequenceViewer, master: Any = None):
        super().__init__(master)
        self.master = master
        self.viewer = viewer
        # widgets
        self._make_widgets()

    def _make_widgets(self):
        self.l_control = tk.Label(self, text="Controls")
        self.l_control.pack(side="top")
        self.b_first = tk.Button(self)
        self.b_first.config(text="|<", command=self.first_state)
        self.b_first.pack(side="left")
        self.b_prev = tk.Button(self)
        self.b_prev.config(text="<<", command=self.prev_state)
        self.b_prev.pack(side="left")
        self.b_next = tk.Button(self)
        self.b_next.config(text=">>", command=self.next_state)
        self.b_next.pack(side="left")
        self.b_last = tk.Button(self)
        self.b_last.config(text=">|", command=self.last_state)
        self.b_last.pack(side="left")
        self.b_col = tk.Button(self)

    def prev_state(self):
        self.viewer.prev_state()

    def next_state(self):
        self.viewer.next_state()

    def first_state(self):
        self.viewer.first_state()

    def last_state(self):
        self.viewer.last_state()


class SeqViewerStateFrame(tk.Frame, View):
    def __init__(self, viewer: SequenceViewer, master: Any = None):
        super().__init__(master)
        viewer.attach(self)
        self._make_widgets()

    def _make_widgets(self):
        self.statevar = tk.StringVar()
        self.l_name = tk.Label(self, text="Current state:")
        self.l_state = tk.Label(self, textvariable=self.statevar)
        self.l_name.pack(side="left")
        self.l_state.pack(side="left")

    def update_view(self, sub: SequenceViewer):
        state = sub.current_state()
        self.statevar.set(str(state))


app = SeqViewerApp()
app.mainloop()
