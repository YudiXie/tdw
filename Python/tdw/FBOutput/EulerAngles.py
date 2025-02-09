# automatically generated by the FlatBuffers compiler, do not modify

# namespace: FBOutput

import tdw.flatbuffers

class EulerAngles(object):
    __slots__ = ['_tab']

    @classmethod
    def GetRootAsEulerAngles(cls, buf, offset):
        n = tdw.flatbuffers.encode.Get(tdw.flatbuffers.packer.uoffset, buf, offset)
        x = EulerAngles()
        x.Init(buf, n + offset)
        return x

    # EulerAngles
    def Init(self, buf, pos):
        self._tab = tdw.flatbuffers.table.Table(buf, pos)

    # EulerAngles
    def Ids(self, j):
        o = tdw.flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(4))
        if o != 0:
            a = self._tab.Vector(o)
            return self._tab.Get(tdw.flatbuffers.number_types.Int32Flags, a + tdw.flatbuffers.number_types.UOffsetTFlags.py_type(j * 4))
        return 0

    # EulerAngles
    def IdsAsNumpy(self):
        o = tdw.flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(4))
        if o != 0:
            return self._tab.GetVectorAsNumpy(tdw.flatbuffers.number_types.Int32Flags, o)
        return 0

    # EulerAngles
    def IdsLength(self):
        o = tdw.flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(4))
        if o != 0:
            return self._tab.VectorLen(o)
        return 0

    # EulerAngles
    def Rotations(self, j):
        o = tdw.flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(6))
        if o != 0:
            a = self._tab.Vector(o)
            return self._tab.Get(tdw.flatbuffers.number_types.Float32Flags, a + tdw.flatbuffers.number_types.UOffsetTFlags.py_type(j * 4))
        return 0

    # EulerAngles
    def RotationsAsNumpy(self):
        o = tdw.flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(6))
        if o != 0:
            return self._tab.GetVectorAsNumpy(tdw.flatbuffers.number_types.Float32Flags, o)
        return 0

    # EulerAngles
    def RotationsLength(self):
        o = tdw.flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(6))
        if o != 0:
            return self._tab.VectorLen(o)
        return 0

def EulerAnglesStart(builder): builder.StartObject(2)
def EulerAnglesAddIds(builder, ids): builder.PrependUOffsetTRelativeSlot(0, tdw.flatbuffers.number_types.UOffsetTFlags.py_type(ids), 0)
def EulerAnglesStartIdsVector(builder, numElems): return builder.StartVector(4, numElems, 4)
def EulerAnglesAddRotations(builder, rotations): builder.PrependUOffsetTRelativeSlot(1, tdw.flatbuffers.number_types.UOffsetTFlags.py_type(rotations), 0)
def EulerAnglesStartRotationsVector(builder, numElems): return builder.StartVector(4, numElems, 4)
def EulerAnglesEnd(builder): return builder.EndObject()
