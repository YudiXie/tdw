# automatically generated by the FlatBuffers compiler, do not modify

# namespace: FBOutput

import tdw.flatbuffers

class IdPassSegmentationColors(object):
    __slots__ = ['_tab']

    @classmethod
    def GetRootAsIdPassSegmentationColors(cls, buf, offset):
        n = tdw.flatbuffers.encode.Get(tdw.flatbuffers.packer.uoffset, buf, offset)
        x = IdPassSegmentationColors()
        x.Init(buf, n + offset)
        return x

    # IdPassSegmentationColors
    def Init(self, buf, pos):
        self._tab = tdw.flatbuffers.table.Table(buf, pos)

    # IdPassSegmentationColors
    def AvatarId(self):
        o = tdw.flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(4))
        if o != 0:
            return self._tab.String(o + self._tab.Pos)
        return None

    # IdPassSegmentationColors
    def SegmentationColors(self, j):
        o = tdw.flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(6))
        if o != 0:
            a = self._tab.Vector(o)
            return self._tab.Get(tdw.flatbuffers.number_types.Uint8Flags, a + tdw.flatbuffers.number_types.UOffsetTFlags.py_type(j * 1))
        return 0

    # IdPassSegmentationColors
    def SegmentationColorsAsNumpy(self):
        o = tdw.flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(6))
        if o != 0:
            return self._tab.GetVectorAsNumpy(tdw.flatbuffers.number_types.Uint8Flags, o)
        return 0

    # IdPassSegmentationColors
    def SegmentationColorsLength(self):
        o = tdw.flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(6))
        if o != 0:
            return self._tab.VectorLen(o)
        return 0

def IdPassSegmentationColorsStart(builder): builder.StartObject(2)
def IdPassSegmentationColorsAddAvatarId(builder, avatarId): builder.PrependUOffsetTRelativeSlot(0, tdw.flatbuffers.number_types.UOffsetTFlags.py_type(avatarId), 0)
def IdPassSegmentationColorsAddSegmentationColors(builder, segmentationColors): builder.PrependUOffsetTRelativeSlot(1, tdw.flatbuffers.number_types.UOffsetTFlags.py_type(segmentationColors), 0)
def IdPassSegmentationColorsStartSegmentationColorsVector(builder, numElems): return builder.StartVector(1, numElems, 1)
def IdPassSegmentationColorsEnd(builder): return builder.EndObject()
