little_endian
proc align {size alignment} {
	set extra [expr $size % $alignment]
	set newExtra [expr $extra > 0 ? $alignment : 0]
	return [expr $size - $extra + $newExtra]
}

proc alignPos {alignment} {
	goto [align [pos] $alignment]
}

proc pptr {name} {
	section $name {
		int32 "m_FileID"
		int64 "m_PathID"
	}
}

proc rectf {name} {
	section $name {
		float "x"
		float "y"
		float "width"
		float "height"
	}
}

proc vector2f {name} {
	section $name {
		float "x"
		float "y"
	}
}

proc vector3f {name} {
	section $name {
		float "x"
		float "y"
		float "z"
	}
}

proc vector4f {name} {
	section $name {
		float "x"
		float "y"
		float "z"
		float "w"
	}
}

set nameLen [uint32 "Name Length"]
str [align $nameLen 4] "utf8" "Name"
rectf "m_Rect"
vector2f "m_Offset"
vector4f "m_Border"
float "m_PixelsToUnits"
vector2f "m_Pivot"
uint32 "m_Extrude"
uint8 "m_IsPolygon"
alignPos 4
section "m_RenderDataKey" {
	uuid "first"
	int64 "second"
}
uint32 "m_AtlasTags.size"
pptr "m_SpriteAtlas"
section "m_RD" {
	pptr "texture"
	pptr "alphaTexture"
	section "m_SubMeshes" {
		set alen [int32 "size"]
		for {set i 0} {$i < $alen} {incr i} {
			section "Submesh" {
				uint32 "firstByte"
				uint32 "indexCount"
				int32 "topology"
				uint32 "firstVertex"
				uint32 "vertexCount"
				section "localAABB" {
					vector3f "m_Center"
					vector3f "m_Extent"
				}
			}
		}
	}
	section "m_IndexBuffer" {
		set alen [int32 "size"]
		for {set i 0} {$i < $alen} {incr i} {
			uint8 "data"
		}
	}
	section "m_VertexData" {
		int32 "m_CurrentChannels"
		uint32 "m_VertexCount"
		section "m_Channels" {
			set alen [int32 "size"]
			for {set i 0} {$i < $alen} {incr i} {
				section "ChannelInfo" {
					uint8 "stream"
					uint8 "offset"
					uint8 "format"
					uint8 "dimension"
				}
			}
		}
		set dlen [uint32 "dataSize"]
		bytes $dlen "data"
	}
	rectf "textureRect"
	vector2f "textureRectOffset"
	vector2f "atlasRectOffset"
	uint32 "settingsRaw"
	vector4f "uvTransform"
	float "downscaleMultiplier"
}

section "m_PhysicsShape" {
	set alen [int32 "size"]
	for {set i 0} {$i < $alen} {incr i} {
		section "Entry" {
			set blen [int32 "size"]
			for {set j 0} {$j < $blen} {incr j} {
				vector2f "data"
			}
		}
	}
}