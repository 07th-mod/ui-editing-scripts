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
uint32 "m_Extrude"

section "m_RD" {
	pptr "texture"
	pptr "alphaTexture"
	section "vertices" {
		set alen [int32 "size"]
		for {set i 0} {$i < $alen} {incr i} {
			vector3f "pos"
		}
	}
	section "indices" {
		set alen [int32 "size"]
		for {set i 0} {$i < $alen} {incr i} {
			uint16 "data"
		}
	}
	rectf "textureRect"
	vector2f "textureRectOffset"
	uint32 "settingsRaw"
	vector4f "uvTransform"
}