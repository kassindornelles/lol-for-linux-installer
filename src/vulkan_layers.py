import cffi

_ffi = cffi.FFI()

_ffi.cdef("""
typedef unsigned int uint32_t;

typedef uint32_t VkResult;

typedef struct VkLayerProperties {
    char        layerName[256];
    uint32_t    specVersion;
    uint32_t    implementationVersion;
    char        description[256];
} VkLayerProperties;

VkResult vkEnumerateInstanceLayerProperties(uint32_t *pPropertyCount, VkLayerProperties *pProperties);
""")

_libvulkan = _ffi.dlopen("libvulkan.so.1")

_cLayerCount = _ffi.new("uint32_t*")
_libvulkan.vkEnumerateInstanceLayerProperties(_cLayerCount, _ffi.NULL)

_cLayers = _ffi.new(f"VkLayerProperties[{_cLayerCount[0]}]")
_libvulkan.vkEnumerateInstanceLayerProperties(_cLayerCount, _cLayers)

LAYERS = [_ffi.string(_cLayers[i].layerName).decode('utf-8') for i in range(_cLayerCount[0])]
