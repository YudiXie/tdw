# automatically generated by the FlatBuffers compiler, do not modify

# namespace: FBOutput

import tdw.flatbuffers

class ReplicantSegmentationColors(object):
    __slots__ = ['_tab']

    @classmethod
    def GetRootAsReplicantSegmentationColors(cls, buf, offset):
        n = tdw.flatbuffers.encode.Get(tdw.flatbuffers.packer.uoffset, buf, offset)
        x = ReplicantSegmentationColors()
        x.Init(buf, n + offset)
        return x

    # ReplicantSegmentationColors
    def Init(self, buf, pos):
        self._tab = tdw.flatbuffers.table.Table(buf, pos)

    # ReplicantSegmentationColors
    def Ids(self, j):
        o = tdw.flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(4))
        if o != 0:
            a = self._tab.Vector(o)
            return self._tab.Get(tdw.flatbuffers.number_types.Int32Flags, a + tdw.flatbuffers.number_types.UOffsetTFlags.py_type(j * 4))
        return 0

    # ReplicantSegmentationColors
    def IdsAsNumpy(self):
        o = tdw.flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(4))
        if o != 0:
            return self._tab.GetVectorAsNumpy(tdw.flatbuffers.number_types.Int32Flags, o)
        return 0

    # ReplicantSegmentationColors
    def IdsLength(self):
        o = tdw.flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(4))
        if o != 0:
            return self._tab.VectorLen(o)
        return 0

    # ReplicantSegmentationColors
    def Colors(self, j):
        o = tdw.flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(6))
        if o != 0:
            a = self._tab.Vector(o)
            return self._tab.Get(tdw.flatbuffers.number_types.Int32Flags, a + tdw.flatbuffers.number_types.UOffsetTFlags.py_type(j * 4))
        return 0

    # ReplicantSegmentationColors
    def ColorsAsNumpy(self):
        o = tdw.flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(6))
        if o != 0:
            return self._tab.GetVectorAsNumpy(tdw.flatbuffers.number_types.Int32Flags, o)
        return 0

    # ReplicantSegmentationColors
    def ColorsLength(self):
        o = tdw.flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(6))
        if o != 0:
            return self._tab.VectorLen(o)
        return 0

def ReplicantSegmentationColorsStart(builder): builder.StartObject(2)
def ReplicantSegmentationColorsAddIds(builder, ids): builder.PrependUOffsetTRelativeSlot(0, tdw.flatbuffers.number_types.UOffsetTFlags.py_type(ids), 0)
def ReplicantSegmentationColorsStartIdsVector(builder, numElems): return builder.StartVector(4, numElems, 4)
def ReplicantSegmentationColorsAddColors(builder, colors): builder.PrependUOffsetTRelativeSlot(1, tdw.flatbuffers.number_types.UOffsetTFlags.py_type(colors), 0)
def ReplicantSegmentationColorsStartColorsVector(builder, numElems): return builder.StartVector(4, numElems, 4)
def ReplicantSegmentationColorsEnd(builder): return builder.EndObject()
