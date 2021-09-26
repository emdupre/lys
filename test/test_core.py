import unittest
import os
import shutil
import numpy as np
import dask.array as da

from ExtendAnalysis.core import SettingDict, Wave, DaskWave


class core_test(unittest.TestCase):
    path = "test/testData"

    def setUp(self):
        os.mkdir(self.path)

    def tearDown(self):
        shutil.rmtree(self.path)

    def test_SettingDict(self):
        # check normal save
        d = SettingDict()
        d["test1"] = "test1"
        d.Save(self.path + "/test.dic")

        # check normal load
        d2 = SettingDict(self.path + "/test.dic")
        self.assertEqual(d2["test1"], "test1")

        # check automatic save
        d2["test1"] = "test2"
        d3 = SettingDict(self.path + "/test.dic")
        self.assertEqual(d3["test1"], "test2")

    def test_WaveAxes(self):
        # without specifing axes
        noaxes = Wave([[1, 2], [3, 4]])
        self.assertEqual(len(noaxes.axes), 2)
        self.assertTrue((noaxes.axes[0] == np.array(None)).all())
        self.assertTrue((noaxes.axes[1] == np.array(None)).all())

        # with specifing axes
        axis1, axis2 = [2, 3, 4], [2, 3]
        w = Wave(np.zeros([3, 2]), axis1, axis2)
        self.assertEqual(len(w.axes), 2)
        self.assertTrue((w.axes[0] == axis1).all())
        self.assertTrue((w.axes[1] == axis2).all())

        # x,y,z
        self.assertTrue((w.x == axis1).all())
        self.assertTrue((w.y == axis2).all())
        w.x = [3, 4, 5]
        self.assertTrue(w.x == [3, 4, 5])

        # invalid axes specified
        with self.assertRaises(TypeError):
            w = Wave(np.zeros([3, 2]), "aaa", [2, 3])

        # axisIsValid method
        self.assertFalse(noaxes.axisIsValid(0))
        self.assertFalse(noaxes.axisIsValid(1))
        self.assertTrue(w.axisIsValid(0))
        self.assertTrue(w.axisIsValid(1))

        # getAxis method
        self.assertTrue((noaxes.getAxis(0) == [0, 1]).all())
        self.assertTrue((w.getAxis(0) == axis1).all())

        # posToPoint method
        w = Wave(np.ones([3, 2]), [1, 2, 3], [3, 4, 5])
        self.assertTrue(w.posToPoint((2, 4)) == (1, 1))
        self.assertTrue(w.posToPoint((1, 2, 3), axis=0) == (0, 1, 2))
        self.assertTrue(w.posToPoint(2, axis=0) == 1)

        # pointToPos method
        w = Wave(np.ones([3, 2]), [1, 2, 3], [3, 4, 5])
        self.assertTrue(w.pointToPos((1, 1)) == (2, 4))
        self.assertTrue(w.pointToPos((0, 1, 2), axis=0) == (1, 2, 3))
        self.assertTrue(w.pointToPos(1, axis=0) == 2)

    def test_WaveNote(self):
        w = Wave([1, 2, 3], name="wave1", key1="item1")
        self.assertEqual(w.note["key1"], "item1")
        w.note["key2"] = 1111
        self.assertEqual(w.note["key2"], 1111)
        self.assertEqual(w.name, "wave1")

    def test_Wave(self):
        # Basic initialization
        w = Wave([1, 2, 3])
        self.assertTrue((w.data == [1, 2, 3]).all())
        w = Wave([1, 2, 3], [0, 1, 2])
        w2 = Wave([w, w], [4, 5])
        self.assertTrue((w2.data == [[1, 2, 3], [1, 2, 3]]).all())
        self.assertTrue((w2.axes[0] == [4, 5]).all())
        self.assertTrue((w2.axes[1] == [0, 1, 2]).all())

        # modification
        self.b = 0

        def invert():
            self.b += 1
        w = Wave([1, 2, 3], [1, 2, 3])
        w.modified.connect(invert)
        w.data = [2, 3, 4]
        self.assertEqual(self.b, 1)
        w.axes[0] = [2, 3, 4]
        self.assertEqual(self.b, 2)
        w.update()
        self.assertEqual(self.b, 3)

        # check save &" load
        path = self.path + "/wave1.npz"
        csv = self.path + "/wave1.csv"
        txt = self.path + "/wave1.txt"
        w = Wave(np.ones([2, 3]), [1, 2], [3, 4, 5], name="wave1")
        w.export(path)
        w.export(csv, type="csv")
        w.export(txt, type="txt")

        w2 = Wave(path)
        self.assertTrue((w.data == w2.data).all())
        self.assertTrue((w.axes[0] == w2.axes[0]).all())
        self.assertTrue((w.axes[1] == w2.axes[1]).all())
        self.assertTrue(w.name == w2.name)

        w2 = Wave.importFrom(path)
        self.assertTrue((w.data == w2.data).all())
        self.assertTrue((w.axes[0] == w2.axes[0]).all())
        self.assertTrue((w.axes[1] == w2.axes[1]).all())
        self.assertTrue(w.name == w2.name)

        w2 = Wave.importFrom(csv)
        self.assertTrue((w.data == w2.data).all())

        w2 = Wave.importFrom(txt)
        self.assertTrue((w.data == w2.data).all())

        # duplicate
        w2 = w.duplicate()
        self.assertTrue((w.data == w2.data).all())
        self.assertTrue((w.axes[0] == w2.axes[0]).all())
        self.assertTrue((w.axes[1] == w2.axes[1]).all())
        self.assertTrue(w.name == w2.name)

    def test_DaskWave(self):
        w = Wave([1, 2, 3], [4, 5, 6], name="wave1")
        # initialization
        dw = DaskWave(w)
        self.assertTrue(w.shape == dw.shape)
        self.assertTrue((w.x == dw.x).all())
        self.assertTrue(w.name == dw.name)

        # compute
        w = dw.compute()
        self.assertTrue(w.shape == dw.shape)
        self.assertTrue((w.x == dw.x).all())
        self.assertTrue(w.name == dw.name)
        self.assertTrue((w.data == [1, 2, 3]).all())

        # initializa from array
        dw = DaskWave([4, 5, 6])
        self.assertTrue((dw.compute().data == [4, 5, 6]).all())

        # initialize from dask.array
        dw = DaskWave(da.from_array([7, 8, 9]))
        self.assertTrue((dw.compute().data == [7, 8, 9]).all())

        # initialize from DaskWave
        dw = DaskWave(dw)
        self.assertTrue((dw.compute().data == [7, 8, 9]).all())

        # duplicate
        dw = dw.duplicate()
        self.assertTrue((dw.compute().data == [7, 8, 9]).all())
