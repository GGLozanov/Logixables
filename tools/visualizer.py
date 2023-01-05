from models.logixable import Logixable
from data_structs.queue import Queue, QueueNode
from tkinter import *

class LogixableVisualizer:
    __tree_level_offset = 120
    __node_offset = 90

    def visualize(self, logixable: Logixable):
        win = Tk()
        win.geometry("600x400")
        win.title("'%s' Visualized" % logixable.name)

        c = Canvas(win, width=400, height=400)
        c.pack()

        logixable_tree_root = logixable.definition.expr_tree.root
        node_q = Queue(QueueNode(logixable_tree_root))

        start_coord_x = previous_cur_node_start_coord_x = 150
        start_coord_y = previous_cur_node_start_coord_y = 100
        circle_radius = 20
        level_multiplier = 50
        level = 0
        while not node_q.is_empty():
            cur_node = node_q.dequeue()

            if cur_node.data == logixable_tree_root:
                self.__create_node_circle(start_coord_x, start_coord_y, circle_radius, c)
                c.create_text(start_coord_x, start_coord_y, text=cur_node.data.value, fill="black")

            if cur_node.data.children != None:
                child_l = len(cur_node.data.children)
                for idx, child in enumerate(cur_node.data.children):
                    if child != None:
                        node_q.enqueue(QueueNode(child))
                        node_coord_x = start_coord_x + (level_multiplier * level) + ((idx - (child_l // 2)) * self.__node_offset)
                        node_coord_y = start_coord_y + (level_multiplier * level) + self.__tree_level_offset
                        self.__create_node_circle(node_coord_x, node_coord_y, circle_radius, c)
                        c.create_text(node_coord_x, node_coord_y, text=child.value, fill="black")

                        # node_coord_y - level_multiplier - self.__tree_level_offset
                        c.create_line(node_coord_x, node_coord_y - circle_radius, previous_cur_node_start_coord_x, 
                            previous_cur_node_start_coord_y + circle_radius)
                        # draw node
            previous_cur_node_start_coord_x = node_coord_x
            previous_cur_node_start_coord_y = node_coord_y

            level += 1

        win.mainloop()
        
        pass

    def __create_node_circle(self, x, y, r, c: Canvas):
        x0 = x - r
        y0 = y - r
        x1 = x + r
        y1 = y + r
        return c.create_oval(x0, y0, x1, y1, fill='#DCD')