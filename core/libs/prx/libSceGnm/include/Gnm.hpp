#ifndef CORE_LIBS_PRX_LIBSCEGNM_GNM_HPP
#define CORE_LIBS_PRX_LIBSCEGNM_GNM_HPP

#include <cstdint>
#include <cstddef>
#include <vector>
#include <string>
#include <unordered_map>
#include <vulkan/vulkan.h>

namespace sce {
namespace Gnm {

// Vulkan resource wrappers for GNM resources
struct VulkanBuffer {
    VkBuffer buffer = VK_NULL_HANDLE;
    VkDeviceMemory memory = VK_NULL_HANDLE;
    VkDeviceSize size = 0;
};

struct VulkanTexture {
    VkImage image = VK_NULL_HANDLE;
    VkDeviceMemory memory = VK_NULL_HANDLE;
    VkImageView view = VK_NULL_HANDLE;
    VkFormat format = VK_FORMAT_UNDEFINED;
    uint32_t width = 0;
    uint32_t height = 0;
};

struct VulkanShaderModule {
    VkShaderModule module = VK_NULL_HANDLE;
    std::vector<uint8_t> spirv;
};

// Undefine Windows error macros that conflict with GNM enum values
#ifdef _WIN32
#undef ERROR_INVALID_POINTER
#undef ERROR_INVALID_SIZE
#undef ERROR_INVALID_ENUM
#undef ERROR_OUT_OF_MEMORY
#undef ERROR_NOT_INITIALIZED
#undef ERROR_INVALID_HANDLE
#endif

enum Result : int32_t {
    OK = 0,
    ERROR_INVALID_POINTER = -0x80030001,
    ERROR_INVALID_SIZE = -0x80030002,
    ERROR_INVALID_ENUM = -0x80030003,
    ERROR_OUT_OF_MEMORY = -0x80030004,
    ERROR_NOT_INITIALIZED = -0x80030005,
    ERROR_INVALID_HANDLE = -0x80030006,
};

enum PrimitiveType : uint32_t {
    PRIMITIVE_TYPE_TRIANGLE_LIST = 0,
    PRIMITIVE_TYPE_TRIANGLE_STRIP = 1,
    PRIMITIVE_TYPE_LINE_LIST = 2,
    PRIMITIVE_TYPE_LINE_STRIP = 3,
    PRIMITIVE_TYPE_POINT_LIST = 4,
};

enum BufferType : uint32_t {
    BUFFER_TYPE_VERTEX = 0,
    BUFFER_TYPE_INDEX = 1,
    BUFFER_TYPE_CONSTANT = 2,
    BUFFER_TYPE_RAW = 3,
};

enum ShaderStage : uint32_t {
    SHADER_STAGE_VS = 0,
    SHADER_STAGE_HS = 1,
    SHADER_STAGE_DS = 2,
    SHADER_STAGE_GS = 3,
    SHADER_STAGE_PS = 4,
    SHADER_STAGE_CS = 5,
};

enum ResourceType : uint32_t {
    RESOURCE_TYPE_BUFFER = 0,
    RESOURCE_TYPE_TEXTURE_1D = 1,
    RESOURCE_TYPE_TEXTURE_2D = 2,
    RESOURCE_TYPE_TEXTURE_3D = 3,
    RESOURCE_TYPE_TEXTURE_CUBE = 4,
};

struct Buffer {
    uint64_t gpuAddress = 0;
    uint64_t size = 0;
    BufferType type = BUFFER_TYPE_VERTEX;
    void* cpuAddress = nullptr;
    bool isGpuOwned = false;
    VulkanBuffer vk{};  // Vulkan backend resource
};

struct Texture {
    uint64_t gpuAddress = 0;
    uint64_t size = 0;
    ResourceType type = RESOURCE_TYPE_TEXTURE_2D;
    uint32_t width = 0;
    uint32_t height = 0;
    uint32_t depth = 1;
    uint32_t mipLevels = 1;
    uint32_t arraySize = 1;
    uint32_t format = 0;
    void* cpuAddress = nullptr;
    VulkanTexture vk{};  // Vulkan backend resource
};

struct RenderTarget {
    Texture texture;
    uint32_t width = 0;
    uint32_t height = 0;
    uint32_t format = 0;
    uint32_t mipLevel = 0;
    uint32_t arraySlice = 0;
};

struct DepthStencil {
    Texture texture;
    uint32_t width = 0;
    uint32_t height = 0;
    uint32_t format = 0;
};

struct Sampler {
    uint32_t filterMode = 0;
    uint32_t addressU = 0;
    uint32_t addressV = 0;
    uint32_t addressW = 0;
    uint32_t mipFilterMode = 0;
    uint32_t maxAnisotropy = 1;
    float mipLodBias = 0.0f;
    float minLod = 0.0f;
    float maxLod = 1000.0f;
};

struct Shader {
    ShaderStage stage = SHADER_STAGE_VS;
    std::vector<uint8_t> bytecode;
    uint32_t bytecodeSize = 0;
    void* shaderPtr = nullptr;
    VulkanShaderModule vk{};  // Vulkan backend resource
};

struct CommandBuffer {
    uint64_t gpuAddress = 0;
    uint64_t size = 0;
    uint32_t commandOffset = 0;
    bool submitted = false;
    void* cpuAddress = nullptr;  // CPU-accessible pointer to command data (PC only)
};

// GNM command buffer opcodes (based on PS4 GNM reverse engineering)
enum CmdOpcode : uint32_t {
    CMD_NOP = 0x00,
    CMD_SET_SHADER_VS = 0x01,
    CMD_SET_SHADER_PS = 0x02,
    CMD_SET_VERTEX_BUFFER = 0x03,
    CMD_SET_INDEX_BUFFER = 0x04,
    CMD_SET_CONSTANT_BUFFER = 0x05,
    CMD_SET_TEXTURE = 0x06,
    CMD_SET_SAMPLER = 0x07,
    CMD_SET_RENDER_TARGET = 0x08,
    CMD_SET_DEPTH_STENCIL = 0x09,
    CMD_SET_VIEWPORT = 0x0A,
    CMD_SET_SCISSOR = 0x0B,
    CMD_SET_PRIMITIVE_TYPE = 0x0C,
    CMD_DRAW = 0x0D,
    CMD_DRAW_INDEXED = 0x0E,
    CMD_DRAW_INDIRECT = 0x0F,
    CMD_DRAW_INDEXED_INDIRECT = 0x10,
    CMD_SET_RENDER_TARGET_MASK = 0x11,
    CMD_SET_BLEND_STATE = 0x12,
    CMD_SET_DEPTH_STENCIL_STATE = 0x13,
    CMD_SET_RASTERIZER_STATE = 0x14,
    CMD_SET_STENCIL_REF = 0x15,
    CMD_SET_BLEND_FACTOR = 0x16,
    CMD_DISPATCH = 0x17,
    CMD_DISPATCH_INDIRECT = 0x18,
    CMD_WAIT_ON_ADDRESS = 0x19,
    CMD_WRITE_TO_ADDRESS = 0x1A,
    CMD_QUEUE_EVENT = 0x1B,
    CMD_SET_SHADER_GS = 0x1C,
    CMD_SET_SHADER_HS = 0x1D,
    CMD_SET_SHADER_DS = 0x1E,
    CMD_SET_SHADER_CS = 0x1F,
    CMD_SET_SHADER_RESOURCE = 0x20,
    CMD_SET_UNORDERED_ACCESS_VIEW = 0x21,
    CMD_END_OF_BUFFER = 0xFF,
};

// Command buffer command header
struct GnmCommand {
    uint32_t opcode;
    uint32_t size;  // Size of command data following header (in bytes)
    // Followed by 'size' bytes of command-specific data
};

struct DrawIndexedCmd {
    uint32_t indexCount;
    uint32_t instanceCount;
    uint32_t firstIndex;
    int32_t  vertexOffset;
    uint32_t firstInstance;
};

struct DrawCmd {
    uint32_t vertexCount;
    uint32_t instanceCount;
    uint32_t firstVertex;
    uint32_t firstInstance;
};

struct SetVertexBufferCmd {
    uint32_t slot;
    uint64_t gpuAddress;
    uint64_t size;
    uint32_t stride;
};

struct SetIndexBufferCmd {
    uint64_t gpuAddress;
    uint64_t size;
    uint32_t format;  // 0 = 16-bit, 1 = 32-bit
};

struct SetConstantBufferCmd {
    uint32_t slot;
    uint64_t gpuAddress;
    uint64_t size;
};

struct SetTextureCmd {
    uint32_t slot;
    uint64_t gpuAddress;
    uint32_t width;
    uint32_t height;
    uint32_t format;
    uint32_t mipLevels;
};

struct SetSamplerCmd {
    uint32_t slot;
    uint32_t filterMode;
    uint32_t addressU;
    uint32_t addressV;
    uint32_t addressW;
    uint32_t mipFilterMode;
    uint32_t maxAnisotropy;
    float mipLodBias;
    float minLod;
    float maxLod;
};

struct SetViewportCmd {
    float x;
    float y;
    float width;
    float height;
    float minDepth;
    float maxDepth;
};

struct SetScissorCmd {
    uint32_t x;
    uint32_t y;
    uint32_t width;
    uint32_t height;
};

struct SetPrimitiveTypeCmd {
    uint32_t primitiveType;
};

struct SetRenderTargetCmd {
    uint32_t slot;
    uint64_t gpuAddress;
    uint32_t width;
    uint32_t height;
    uint32_t format;
};

struct DispatchCmd {
    uint32_t threadGroupX;
    uint32_t threadGroupY;
    uint32_t threadGroupZ;
};


struct DrawContext {
    Shader* vsShader = nullptr;
    Shader* hsShader = nullptr;
    Shader* dsShader = nullptr;
    Shader* gsShader = nullptr;
    Shader* psShader = nullptr;
    Shader* csShader = nullptr;
    Buffer* vertexBuffer = nullptr;
    Buffer* indexBuffer = nullptr;
    Buffer* constantBuffers[16] = {};
    uint32_t constantBufferCount = 0;
    Texture* textures[16] = {};
    Sampler* samplers[16] = {};
    uint32_t textureCount = 0;
    RenderTarget renderTarget{};
    DepthStencil depthStencil{};
    PrimitiveType primitiveType = PRIMITIVE_TYPE_TRIANGLE_LIST;
    uint32_t viewportWidth = 0;
    uint32_t viewportHeight = 0;
    uint32_t scissorWidth = 0;
    uint32_t scissorHeight = 0;
};

struct GlobalState {
    bool initialized = false;
    CommandBuffer currentCommandBuffer{};
    DrawContext drawContext{};
    std::vector<CommandBuffer*> submittedBuffers;
    uint32_t frameIndex = 0;
    bool flipPending = false;

    // Vulkan backend state
    VkInstance instance = VK_NULL_HANDLE;
    VkPhysicalDevice physicalDevice = VK_NULL_HANDLE;
    VkDevice device = VK_NULL_HANDLE;
    VkQueue queue = VK_NULL_HANDLE;
    uint32_t queueFamilyIndex = 0;
    VkSwapchainKHR swapchain = VK_NULL_HANDLE;
    std::vector<VkImage> swapchainImages;
    std::vector<VkImageView> swapchainImageViews;
    std::vector<VkFramebuffer> swapchainFramebuffers;
    VkCommandPool commandPool = VK_NULL_HANDLE;
    VkCommandBuffer commandBuffer = VK_NULL_HANDLE;
    VkRenderPass renderPass = VK_NULL_HANDLE;
    VkPipelineCache pipelineCache = VK_NULL_HANDLE;
    VkSemaphore imageAvailableSemaphore = VK_NULL_HANDLE;
    VkSemaphore renderFinishedSemaphore = VK_NULL_HANDLE;
    VkFence inFlightFence = VK_NULL_HANDLE;
    uint32_t currentFrame = 0;
    uint32_t swapchainImageCount = 0;
    VkExtent2D swapchainExtent{};
    VkFormat swapchainImageFormat = VK_FORMAT_UNDEFINED;
    VkPipeline graphicsPipeline = VK_NULL_HANDLE;
    VkPipelineLayout pipelineLayout = VK_NULL_HANDLE;
    VkDescriptorSetLayout descriptorSetLayout = VK_NULL_HANDLE;
    VkDescriptorPool descriptorPool = VK_NULL_HANDLE;
    std::vector<VkDescriptorSet> descriptorSets;

    // Hardcoded shader modules for debugging
    VkShaderModule vertShaderModule = VK_NULL_HANDLE;
    VkShaderModule fragShaderModule = VK_NULL_HANDLE;
};

GlobalState& GetGlobalState();

} // namespace Gnm
} // namespace sce

#endif