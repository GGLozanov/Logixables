from models.logixable import Logixable
from data_structs.queue import Queue, QueueNode
from tkinter import *

class LogixableVisualizer:
    __tree_level_offset = 100
    __node_offset = 40

    def visualize(self, logixable: Logixable):
        win = Tk()
        win.geometry("600x400")
        win.title("'%s' Visualized" % logixable.name)

        c = Canvas(win, width=1600, height=1600)
        c.pack()

        logixable_tree_root = logixable.definition.expr_tree.root
        tree_depth = self.__calc_tree_depth(logixable_tree_root)
        node_q = Queue(QueueNode(logixable_tree_root))

        start_coord_x = 350
        start_coord_y = 100

        coords_q = Queue(QueueNode((start_coord_x, start_coord_y)))

        circle_radius = 20
        level_multiplier = 5
        level = 0
        while not node_q.is_empty():
            cur_node = node_q.dequeue()

            if cur_node.data == logixable_tree_root:
                self.__create_node_circle(start_coord_x, start_coord_y, circle_radius, c)
                c.create_text(start_coord_x, start_coord_y, text=cur_node.data.value, fill="black")

            if cur_node.data.children != None:
                child_l = len(cur_node.data.children)
                previous_cur_node_start_coords = coords_q.dequeue().data
                previous_cur_node_start_coord_x = previous_cur_node_start_coords[0]
                previous_cur_node_start_coord_y = previous_cur_node_start_coords[1] 
                for idx, child in enumerate(cur_node.data.children):
                    if child != None:
                        node_q.enqueue(QueueNode(child))
                        node_coord_x = previous_cur_node_start_coord_x + (-1 if idx < child_l // 2 else 1) * self.__node_offset * (tree_depth - level)
                        node_coord_y = previous_cur_node_start_coord_y + (level_multiplier * level) + self.__tree_level_offset
                        self.__create_node_circle(node_coord_x, node_coord_y, circle_radius, c)
                        c.create_text(node_coord_x, node_coord_y, text=child.value if not isinstance(child.value, Logixable) else child.value.name, fill="black")

                        # node_coord_y - level_multiplier - self.__tree_level_offset
                        c.create_line(node_coord_x, node_coord_y - circle_radius, previous_cur_node_start_coord_x, 
                            previous_cur_node_start_coord_y + circle_radius)

                        if child.children != None:
                            coords_q.enqueue(QueueNode((node_coord_x, node_coord_y)))
                            # previous_cur_node_start_coord_x = node_coord_x
                            # previous_cur_node_start_coord_y = node_coord_y

            level += 1

        win.mainloop()

    def __create_node_circle(self, x, y, r, c: Canvas):
        x0 = x - r
        y0 = y - r
        x1 = x + r
        y1 = y + r
        return c.create_oval(x0, y0, x1, y1, fill='#DCD')

    def __calc_tree_depth(self, node):
        if node is None or node.children is None:
            return 0

        child_max = -1
        for child in node.children:
            c_depth = self.__calc_tree_depth(child)
            if child_max < c_depth:
                child_max = c_depth

        # account for root
        return child_max + 1
 