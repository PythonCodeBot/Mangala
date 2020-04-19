"""link list"""

from __future__ import annotations
from typing import TypeVar, Generic

DataType = TypeVar('DataType')


class Node(Generic[DataType]):
    """
    Node for two side link list
    """
    data: DataType  # the data of the Node
    right_node: Node  # the right or next node
    left_node: Node  # the left or before node
    parallel_node: Node  # the parallel enemy pit

    def __init__(self, node_data: DataType = None) -> None:
        """
        init the fields
        :param node_data: the data of the class
        """
        self.data = node_data
        self.right_node = None
        self.left_node = None

    def insert_right(self, data: DataType) -> Node[DataType]:
        """
        Insert to the right new data
        :param data: the data of the new node
        :return: the new node
        """
        self.right_node = Node(data)
        self.right_node.left_node = self  # connect the new node to this node
        return self.right_node

    def insert_left(self, data: DataType) -> Node[DataType]:
        """
        Insert to the left new data
        :param data: the data of the new node
        :return: the new node
        """
        self.left_node = Node(data)
        self.left_node.right_node = self  # connect the new node to this node
        return self.left_node


class LinkList(Generic[DataType]):
    """
    link list of two side. right and left
    """
    most_right: Node[DataType]  # most right node
    most_left: Node[DataType]  # most right node
    start: Node[DataType]  # start of the list

    def __init__(self, data: DataType):
        """
        init the list
        :param data: the data of start node of the list
        """
        self.start = Node(data)
        self.most_left = self.start
        self.most_right = self.start

    def push_right(self, data: DataType) -> Node[DataType]:
        """
        push to the most right
        :param data: the data to put in the list
        :return: the new node
        """
        self.most_right.insert_right(data)
        self.most_right = self.most_right.right_node
        return self.most_right

    def push_left(self, data: DataType) -> Node[DataType]:
        """
        push to the most left
        :param data: the data to put in the list
        :return: the new node
        """
        self.most_left.insert_left(data)
        self.most_left = self.most_left.left_node
        return self.most_left

    def make_looped(self) -> None:
        """
        close the list and make the list looped.
        :return: None
        """
        self.most_right.right_node = self.most_left
        self.most_left.left_node = self.most_right
