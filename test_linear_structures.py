"""
Unit Tests for Phase 1 Linear Data Structures (Linked List, Stack, Queue)
File: tests/test_linear_structures.py
"""

import unittest
from core.linked_list import SinglyLinkedList
from core.stack import LinkedStack
from core.queue import LinkedQueue


class TestSinglyLinkedList(unittest.TestCase):

    def setUp(self):
        self.ll = SinglyLinkedList()

    def test_insert_front_and_rear(self):
        self.ll.insert_front(10)
        self.ll.insert_front(5)
        self.ll.insert_rear(20)
        self.ll.insert_rear(30)

        # Expected list: [5, 10, 20, 30]
        self.assertEqual(len(self.ll), 4)
        self.assertEqual(self.ll.to_list(), [5, 10, 20, 30])
        self.assertEqual(self.ll.head.data, 5)
        self.assertEqual(self.ll.tail.data, 30)

    def test_insert_at_index(self):
        self.ll.insert_rear("A")
        self.ll.insert_rear("C")

        # Insert "B" at index 1
        success = self.ll.insert_at(1, "B")
        self.assertTrue(success)
        self.assertEqual(self.ll.to_list(), ["A", "B", "C"])

        # Insert at 0 (front)
        self.ll.insert_at(0, "START")
        self.assertEqual(self.ll.to_list(), ["START", "A", "B", "C"])

        # Insert at invalid index
        self.assertFalse(self.ll.insert_at(99, "INVALID"))

    def test_delete_operations(self):
        for val in [1, 2, 3, 4, 5]:
            self.ll.insert_rear(val)

        # Delete front
        popped_front = self.ll.delete_front()
        self.assertEqual(popped_front, 1)
        self.assertEqual(self.ll.to_list(), [2, 3, 4, 5])

        # Delete rear
        popped_rear = self.ll.delete_rear()
        self.assertEqual(popped_rear, 5)
        self.assertEqual(self.ll.to_list(), [2, 3, 4])

        # Delete by key (middle element 3)
        deleted = self.ll.delete_by_key(lambda x: x == 3)
        self.assertEqual(deleted, 3)
        self.assertEqual(self.ll.to_list(), [2, 4])

        # Delete at index
        at_idx = self.ll.delete_at(1)
        self.assertEqual(at_idx, 4)
        self.assertEqual(self.ll.to_list(), [2])

        # Delete last remaining
        self.ll.delete_front()
        self.assertTrue(self.ll.is_empty())
        self.assertIsNone(self.ll.head)
        self.assertIsNone(self.ll.tail)

    def test_search_and_get_at(self):
        self.ll.insert_rear({"id": "MCA-01", "name": "Alice"})
        self.ll.insert_rear({"id": "MCA-02", "name": "Bob"})

        found = self.ll.search(lambda item: item["id"] == "MCA-02")
        self.assertIsNotNone(found)
        self.assertEqual(found["name"], "Bob")

        self.assertEqual(self.ll.get_at(0)["id"], "MCA-01")
        self.assertIsNone(self.ll.get_at(5))

    def test_in_place_reverse(self):
        for i in range(1, 6):
            self.ll.insert_rear(i)

        self.assertEqual(self.ll.to_list(), [1, 2, 3, 4, 5])
        self.ll.reverse()
        self.assertEqual(self.ll.to_list(), [5, 4, 3, 2, 1])
        self.assertEqual(self.ll.head.data, 5)
        self.assertEqual(self.ll.tail.data, 1)


class TestLinkedStack(unittest.TestCase):

    def setUp(self):
        self.stack = LinkedStack()

    def test_lifo_push_pop(self):
        self.assertTrue(self.stack.is_empty())

        self.stack.push("Page 1")
        self.stack.push("Page 2")
        self.stack.push("Page 3")

        self.assertEqual(len(self.stack), 3)
        self.assertEqual(self.stack.peek(), "Page 3")

        self.assertEqual(self.stack.pop(), "Page 3")
        self.assertEqual(self.stack.pop(), "Page 2")
        self.assertEqual(self.stack.pop(), "Page 1")
        self.assertTrue(self.stack.is_empty())

    def test_empty_stack_exceptions(self):
        with self.assertRaises(IndexError):
            self.stack.pop()

        with self.assertRaises(IndexError):
            self.stack.peek()


class TestLinkedQueue(unittest.TestCase):

    def setUp(self):
        self.queue = LinkedQueue()

    def test_fifo_enqueue_dequeue(self):
        self.assertTrue(self.queue.is_empty())

        self.queue.enqueue("Customer 1")
        self.queue.enqueue("Customer 2")
        self.queue.enqueue("Customer 3")

        self.assertEqual(len(self.queue), 3)
        self.assertEqual(self.queue.peek(), "Customer 1")

        self.assertEqual(self.queue.dequeue(), "Customer 1")
        self.assertEqual(self.queue.dequeue(), "Customer 2")
        self.assertEqual(self.queue.dequeue(), "Customer 3")
        self.assertTrue(self.queue.is_empty())

    def test_empty_queue_exceptions(self):
        with self.assertRaises(IndexError):
            self.queue.dequeue()

        with self.assertRaises(IndexError):
            self.queue.peek()


if __name__ == "__main__":
    unittest.main()
