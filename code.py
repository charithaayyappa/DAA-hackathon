"""
Hospital Patient Priority Queue  (simple heap version)
------------------------------------------------------
Rule: higher priority is treated first (5 = critical ... 1 = minor).
      Same priority -> the patient who arrived first goes first.

Data structure: a binary heap stored in a Python list.
  - index 0 (the root) is always the NEXT patient to be treated
  - parent of index i   -> (i - 1) // 2
  - children of index i -> 2*i + 1 (left), 2*i + 2 (right)

A small dictionary (self.where) remembers each patient's position in the
heap, so a patient can be found instantly when the priority changes.

Operations:  add O(log n) | peek O(1) | treat_next O(log n) | change_priority O(log n)
"""


class Patient:
    def __init__(self, pid, name, priority, arrival):
        self.pid = pid              # patient ID (P1, P2, ... or given by the user)
        self.name = name
        self.priority = priority    # 1..5
        self.arrival = arrival      # arrival number, used to break ties

    def rank(self):
        # Smaller rank = treated earlier.
        # -priority puts priority 5 before priority 1; arrival breaks ties.
        return (-self.priority, self.arrival)

    def __str__(self):
        return f"{self.pid} {self.name} (Priority {self.priority})"


class HospitalQueue:
    def __init__(self):
        self.heap = []        # the heap itself
        self.where = {}       # patient ID -> index in self.heap
        self.arrivals = 0     # counter that only goes up

    # ---------- heap helpers ----------
    def _swap(self, i, j):
        self.heap[i], self.heap[j] = self.heap[j], self.heap[i]
        self.where[self.heap[i].pid] = i      # keep the position map correct
        self.where[self.heap[j].pid] = j

    def _sift_up(self, i):
        """Move a patient UP while he/she outranks the parent."""
        while i > 0:
            parent = (i - 1) // 2
            if self.heap[i].rank() < self.heap[parent].rank():
                self._swap(i, parent)
                i = parent
            else:
                break

    def _sift_down(self, i):
        """Move a patient DOWN while a child outranks him/her."""
        n = len(self.heap)
        while True:
            left, right, best = 2 * i + 1, 2 * i + 2, i
            if left < n and self.heap[left].rank() < self.heap[best].rank():
                best = left
            if right < n and self.heap[right].rank() < self.heap[best].rank():
                best = right
            if best == i:
                break
            self._swap(i, best)
            i = best

    @staticmethod
    def _valid_priority(priority):
        return isinstance(priority, int) and not isinstance(priority, bool) and 1 <= priority <= 5

    # ---------- operations ----------
    def add(self, name, priority, pid=None):
        """Put the patient at the end, then sift up. O(log n)."""
        if not name or not str(name).strip():
            raise ValueError("Name cannot be empty.")
        if not self._valid_priority(priority):
            raise ValueError("Priority must be a whole number from 1 to 5.")
        self.arrivals += 1
        if pid is None:
            pid = f"P{self.arrivals}"
        if pid in self.where:
            self.arrivals -= 1
            raise ValueError(f"Patient ID {pid} already exists.")
        patient = Patient(pid, str(name).strip(), priority, self.arrivals)
        self.heap.append(patient)
        self.where[pid] = len(self.heap) - 1
        self._sift_up(len(self.heap) - 1)
        return patient

    def peek(self):
        """Look at the next patient without removing. O(1). None if empty."""
        return self.heap[0] if self.heap else None

    def treat_next(self):
        """Remove and return the root patient. O(log n). None if empty."""
        if not self.heap:
            return None
        top = self.heap[0]
        last = self.heap.pop()              # take the last patient out
        del self.where[top.pid]
        if self.heap:
            self.heap[0] = last             # put him/her at the root
            self.where[last.pid] = 0
            self._sift_down(0)              # move down to the right place
        return top

    def change_priority(self, pid, new_priority):
        """Change a waiting patient's priority. O(log n). False if ID unknown."""
        if not self._valid_priority(new_priority):
            raise ValueError("Priority must be a whole number from 1 to 5.")
        if pid not in self.where:
            return False
        i = self.where[pid]                 # direct lookup, no searching
        self.heap[i].priority = new_priority
        self._sift_up(i)                    # may need to go up...
        self._sift_down(self.where[pid])    # ...or down (only one will move)
        return True

    def waiting_list(self):
        """Everyone in treatment order (the heap itself is not changed)."""
        return sorted(self.heap, key=lambda p: p.rank())

    def __len__(self):
        return len(self.heap)


# ------------------------------------------------------------------
# Demo
# ------------------------------------------------------------------
def show(queue):
    for number, p in enumerate(queue.waiting_list(), start=1):
        print(f"  {number}. {p}")


def demo():
    queue = HospitalQueue()
    print("Treat from empty queue ->", queue.treat_next())

    for name, priority in [("x", 3), ("y", 5), ("z", 3),
                           ("p", 1), ("q", 4), ("r", 2)]:
        p = queue.add(name, priority)
        print(f"Added {p}   -> next: {queue.peek().name}")

    print("\nTreatment order (x before z: same priority, arrived first):")
    show(queue)

    print("\np gets worse: priority 1 -> 5")
    queue.change_priority("P4", 5)
    show(queue)

    print("\nEdge cases:")
    for label, action in [("empty name", lambda: queue.add("  ", 3)),
                          ("priority 9", lambda: queue.add("s", 9)),
                          ("duplicate ID", lambda: queue.add("t", 2, pid="P1")),
                          ("unknown ID", lambda: queue.change_priority("P99", 3))]:
        try:
            print(f"  {label}: ->", action())
        except ValueError as e:
            print(f"  {label}: error - {e}")

    print("\nTreating everyone:")
    turn = 1
    while len(queue):
        patient = queue.treat_next()
        print(f"  {turn}. Treated: {patient}  | still waiting: {len(queue)}")
        turn += 1


if __name__ == "__main__":
    demo()