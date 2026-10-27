#include "prx/libSceGnm/include/Gnm.hpp"
#include "prx/libc/include/General.hpp"
#include "prx/libSceVideoOut/include/VideoOutWindow.hpp"
#include "Recompiler.hpp"
#include <vulkan/vulkan.h>
#include <SDL2/SDL.h>
#include <SDL2/SDL_vulkan.h>
#include <cstring>
#include <stdexcept>
#include <set>
#include <iostream>
#include <algorithm>

namespace sce {
namespace Gnm {

static bool CheckDeviceExtensionSupport(VkPhysicalDevice device, const std::vector<const char*>& requiredExtensions) {
    uint32_t extensionCount = 0;
    vkEnumerateDeviceExtensionProperties(device, nullptr, &extensionCount, nullptr);
    std::vector<VkExtensionProperties> availableExtensions(extensionCount);
    vkEnumerateDeviceExtensionProperties(device, nullptr, &extensionCount, availableExtensions.data());
    for (const auto& required : requiredExtensions) {
        bool found = false;
        for (const auto& available : availableExtensions) {
            if (strcmp(required, available.extensionName) == 0) { found = true; break; }
        }
        if (!found) return false;
    }
    return true;
}

static uint32_t FindMemoryType(VkPhysicalDevice physicalDevice, uint32_t typeFilter, VkMemoryPropertyFlags properties) {
    VkPhysicalDeviceMemoryProperties memProperties;
    vkGetPhysicalDeviceMemoryProperties(physicalDevice, &memProperties);
    for (uint32_t i = 0; i < memProperties.memoryTypeCount; i++) {
        if ((typeFilter & (1 << i)) && (memProperties.memoryTypes[i].propertyFlags & properties) == properties) {
            return i;
        }
    }
    throw std::runtime_error("failed to find suitable memory type!");
}

// Hardcoded SPIR-V shaders for debugging (compiled with glslangValidator)
static const uint32_t vert_spirv[] = {
    0x07230203, 0x00010000, 0x0008000b, 0x0000002a, 0x00000000,
    0x00020011, 0x00000001, 0x0006000b, 0x00000001, 0x4c534c47,
    0x6474732e, 0x3035342e, 0x00000000, 0x0003000e, 0x00000000,
    0x00000001, 0x0008000f, 0x00000000, 0x00000004, 0x6e69616d,
    0x00000000, 0x00000008, 0x00000016, 0x00000028, 0x00030003,
    0x00000002, 0x000001c2, 0x00040005, 0x00000004, 0x6e69616d,
    0x00000000, 0x00060005, 0x00000008, 0x565f6c67, 0x65747265,
    0x646e4978, 0x00007865, 0x00060005, 0x00000014, 0x505f6c67,
    0x65767265, 0x78657472, 0x00000000, 0x00060006, 0x00000014,
    0x00000000, 0x505f6c67, 0x7469736f, 0x006e6f69, 0x00070006,
    0x00000014, 0x00000001, 0x505f6c67, 0x746e696f, 0x657a6953,
    0x00000000, 0x00070006, 0x00000014, 0x00000002, 0x435f6c67,
    0x4470696c, 0x61747369, 0x0065636e, 0x00070006, 0x00000014,
    0x00000003, 0x435f6c67, 0x446c6c75, 0x61747369, 0x0065636e,
    0x00030005, 0x00000016, 0x00000000, 0x00050005, 0x00000028,
    0x67617266, 0x6f6c6f43, 0x00000072, 0x00040047, 0x00000008,
    0x0000000b, 0x0000002a, 0x00030047, 0x00000014, 0x00000002,
    0x00050048, 0x00000014, 0x00000000, 0x0000000b, 0x00000000,
    0x00050048, 0x00000014, 0x00000001, 0x0000000b, 0x00000001,
    0x00050048, 0x00000014, 0x00000002, 0x0000000b, 0x00000003,
    0x00050048, 0x00000014, 0x00000003, 0x0000000b, 0x00000004,
    0x00040047, 0x00000028, 0x0000001e, 0x00000000, 0x00020013,
    0x00000002, 0x00030021, 0x00000003, 0x00000002, 0x00040015,
    0x00000006, 0x00000020, 0x00000001, 0x00040020, 0x00000007,
    0x00000001, 0x00000006, 0x0004003b, 0x00000007, 0x00000008,
    0x00000001, 0x0004002b, 0x00000006, 0x0000000a, 0x00000000,
    0x00020014, 0x0000000b, 0x00030016, 0x0000000f, 0x00000020,
    0x00040017, 0x00000010, 0x0000000f, 0x00000004, 0x00040015,
    0x00000011, 0x00000020, 0x00000000, 0x0004002b, 0x00000011,
    0x00000012, 0x00000001, 0x0004001c, 0x00000013, 0x0000000f,
    0x00000012, 0x0006001e, 0x00000014, 0x00000010, 0x0000000f,
    0x00000013, 0x00000013, 0x00040020, 0x00000015, 0x00000003,
    0x00000014, 0x0004003b, 0x00000015, 0x00000016, 0x00000003,
    0x0004002b, 0x0000000f, 0x00000017, 0xbf800000, 0x0004002b,
    0x0000000f, 0x00000018, 0x00000000, 0x0004002b, 0x0000000f,
    0x00000019, 0x3f800000, 0x0007002c, 0x00000010, 0x0000001a,
    0x00000017, 0x00000017, 0x00000018, 0x00000019, 0x00040020,
    0x0000001b, 0x00000003, 0x00000010, 0x0004002b, 0x00000006,
    0x0000001f, 0x00000001, 0x0007002c, 0x00000010, 0x00000023,
    0x00000019, 0x00000017, 0x00000018, 0x00000019, 0x0007002c,
    0x00000010, 0x00000026, 0x00000018, 0x00000019, 0x00000018,
    0x00000019, 0x0004003b, 0x0000001b, 0x00000028, 0x00000003,
    0x0007002c, 0x00000010, 0x00000029, 0x00000019, 0x00000018,
    0x00000018, 0x00000019, 0x00050036, 0x00000002, 0x00000004,
    0x00000000, 0x00000003, 0x000200f8, 0x00000005, 0x0004003d,
    0x00000006, 0x00000009, 0x00000008, 0x000500aa, 0x0000000b,
    0x0000000c, 0x00000009, 0x0000000a, 0x000300f7, 0x0000000e,
    0x00000000, 0x000400fa, 0x0000000c, 0x0000000d, 0x0000001d,
    0x000200f8, 0x0000000d, 0x00050041, 0x0000001b, 0x0000001c,
    0x00000016, 0x0000000a, 0x0003003e, 0x0000001c, 0x0000001a,
    0x000200f9, 0x0000000e, 0x000200f8, 0x0000001d, 0x0004003d,
    0x00000006, 0x0000001e, 0x00000008, 0x000500aa, 0x0000000b,
    0x00000020, 0x0000001e, 0x0000001f, 0x000300f7, 0x00000022,
    0x00000000, 0x000400fa, 0x00000020, 0x00000021, 0x00000025,
    0x000200f8, 0x00000021, 0x00050041, 0x0000001b, 0x00000024,
    0x00000016, 0x0000000a, 0x0003003e, 0x00000024, 0x00000023,
    0x000200f9, 0x00000022, 0x000200f8, 0x00000025, 0x00050041,
    0x0000001b, 0x00000027, 0x00000016, 0x0000000a, 0x0003003e,
    0x00000027, 0x00000026, 0x000200f9, 0x00000022, 0x000200f8,
    0x00000022, 0x000200f9, 0x0000000e, 0x000200f8, 0x0000000e,
    0x0003003e, 0x00000028, 0x00000029, 0x000100fd, 0x00010038
};

static const uint32_t frag_spirv[] = {
    0x07230203, 0x00010000, 0x0008000b, 0x0000000d, 0x00000000,
    0x00020011, 0x00000001, 0x0006000b, 0x00000001, 0x4c534c47,
    0x6474732e, 0x3035342e, 0x00000000, 0x0003000e, 0x00000000,
    0x00000001, 0x0007000f, 0x00000004, 0x00000004, 0x6e69616d,
    0x00000000, 0x00000009, 0x0000000b, 0x00030010, 0x00000004,
    0x00000007, 0x00030003, 0x00000002, 0x000001c2, 0x00040005,
    0x00000004, 0x6e69616d, 0x00000000, 0x00050005, 0x00000009,
    0x4374756f, 0x726f6c6f, 0x00000000, 0x00050005, 0x0000000b,
    0x67617266, 0x6f6c6f43, 0x00000072, 0x00040047, 0x00000009,
    0x0000001e, 0x00000000, 0x00040047, 0x0000000b, 0x0000001e,
    0x00000000, 0x00020013, 0x00000002, 0x00030021, 0x00000003,
    0x00000002, 0x00030016, 0x00000006, 0x00000020, 0x00040017,
    0x00000007, 0x00000006, 0x00000004, 0x00040020, 0x00000008,
    0x00000003, 0x00000007, 0x0004003b, 0x00000008, 0x00000009,
    0x00000003, 0x00040020, 0x0000000a, 0x00000001, 0x00000007,
    0x0004003b, 0x0000000a, 0x0000000b, 0x00000001, 0x00050036,
    0x00000002, 0x00000004, 0x00000000, 0x00000003, 0x000200f8,
    0x00000005, 0x0004003d, 0x00000007, 0x0000000c, 0x0000000b,
    0x0003003e, 0x00000009, 0x0000000c, 0x000100fd, 0x00010038
};

static VkResult InitVulkanInstance(GlobalState& state);
static VkResult InitVulkanInstance(GlobalState& state) {
    VkApplicationInfo appInfo{};
    appInfo.sType = VK_STRUCTURE_TYPE_APPLICATION_INFO;
    appInfo.pApplicationName = "AnyPS4 GNM Port";
    appInfo.applicationVersion = VK_MAKE_VERSION(1, 0, 0);
    appInfo.pEngineName = "AnyPS4";
    appInfo.engineVersion = VK_MAKE_VERSION(1, 0, 0);
    appInfo.apiVersion = VK_API_VERSION_1_2;
    const std::vector<const char*> extensions = {
        VK_KHR_SURFACE_EXTENSION_NAME,
    };
    VkInstanceCreateInfo createInfo{};
    createInfo.sType = VK_STRUCTURE_TYPE_INSTANCE_CREATE_INFO;
    createInfo.pApplicationInfo = &appInfo;
    createInfo.enabledExtensionCount = static_cast<uint32_t>(extensions.size());
    createInfo.ppEnabledExtensionNames = extensions.data();
    return vkCreateInstance(&createInfo, nullptr, &state.instance);
}

// Forward declaration for shader module creation
static VkShaderModule CreateVulkanShaderModule(GlobalState& state, const std::vector<uint32_t>& spirv);

static VkResult PickPhysicalDevice(GlobalState& state) {
    uint32_t deviceCount = 0;
    vkEnumeratePhysicalDevices(state.instance, &deviceCount, nullptr);
    if (deviceCount == 0) return VK_ERROR_INITIALIZATION_FAILED;
    std::vector<VkPhysicalDevice> devices(deviceCount);
    vkEnumeratePhysicalDevices(state.instance, &deviceCount, devices.data());
    for (const auto& device : devices) {
        VkPhysicalDeviceProperties props;
        vkGetPhysicalDeviceProperties(device, &props);
        if (props.deviceType == VK_PHYSICAL_DEVICE_TYPE_DISCRETE_GPU ||
            props.deviceType == VK_PHYSICAL_DEVICE_TYPE_INTEGRATED_GPU) {
            state.physicalDevice = device;
            break;
        }
    }
    if (state.physicalDevice == VK_NULL_HANDLE && deviceCount > 0) {
        state.physicalDevice = devices[0];
    }
    return state.physicalDevice ? VK_SUCCESS : VK_ERROR_INITIALIZATION_FAILED;
}

static VkResult CreateLogicalDevice(GlobalState& state) {
    uint32_t queueFamilyCount = 0;
    vkGetPhysicalDeviceQueueFamilyProperties(state.physicalDevice, &queueFamilyCount, nullptr);
    std::vector<VkQueueFamilyProperties> queueFamilies(queueFamilyCount);
    vkGetPhysicalDeviceQueueFamilyProperties(state.physicalDevice, &queueFamilyCount, queueFamilies.data());
    for (uint32_t i = 0; i < queueFamilyCount; i++) {
        if (queueFamilies[i].queueFlags & VK_QUEUE_GRAPHICS_BIT) {
            state.queueFamilyIndex = i;
            break;
        }
    }
    float queuePriority = 1.0f;
    VkDeviceQueueCreateInfo queueCreateInfo{};
    queueCreateInfo.sType = VK_STRUCTURE_TYPE_DEVICE_QUEUE_CREATE_INFO;
    queueCreateInfo.queueFamilyIndex = state.queueFamilyIndex;
    queueCreateInfo.queueCount = 1;
    queueCreateInfo.pQueuePriorities = &queuePriority;
    const std::vector<const char*> deviceExtensions = {
        VK_KHR_SWAPCHAIN_EXTENSION_NAME,
    };
    VkPhysicalDeviceFeatures deviceFeatures{};
    deviceFeatures.samplerAnisotropy = VK_TRUE;
    VkDeviceCreateInfo createInfo{};
    createInfo.sType = VK_STRUCTURE_TYPE_DEVICE_CREATE_INFO;
    createInfo.pQueueCreateInfos = &queueCreateInfo;
    createInfo.queueCreateInfoCount = 1;
    createInfo.pEnabledFeatures = &deviceFeatures;
    createInfo.enabledExtensionCount = static_cast<uint32_t>(deviceExtensions.size());
    createInfo.ppEnabledExtensionNames = deviceExtensions.data();
    VkResult result = vkCreateDevice(state.physicalDevice, &createInfo, nullptr, &state.device);
    if (result != VK_SUCCESS) return result;
    vkGetDeviceQueue(state.device, state.queueFamilyIndex, 0, &state.queue);
    return VK_SUCCESS;
}

static VkResult CreateSwapchain(GlobalState& state, SDL_Window* window) {
    int w, h;
    SDL_GetWindowSize(window, &w, &h);

    VkSurfaceKHR surface;
    if (!SDL_Vulkan_CreateSurface(window, state.instance, &surface)) {
        APS5_LOG_OUT("[GNM] SDL_Vulkan_CreateSurface failed: %s\n", SDL_GetError());
        return VK_ERROR_INITIALIZATION_FAILED;
    }

    VkSurfaceCapabilitiesKHR caps;
    vkGetPhysicalDeviceSurfaceCapabilitiesKHR(state.physicalDevice, surface, &caps);

    state.swapchainExtent = caps.currentExtent;

    VkSurfaceFormatKHR surfaceFormat;
    uint32_t formatCount;
    vkGetPhysicalDeviceSurfaceFormatsKHR(state.physicalDevice, surface, &formatCount, nullptr);
    std::vector<VkSurfaceFormatKHR> formats(formatCount);
    vkGetPhysicalDeviceSurfaceFormatsKHR(state.physicalDevice, surface, &formatCount, formats.data());
    surfaceFormat = formats[0];
    if (surfaceFormat.format == VK_FORMAT_UNDEFINED) {
        surfaceFormat.format = VK_FORMAT_B8G8R8A8_UNORM;
        surfaceFormat.colorSpace = VK_COLOR_SPACE_SRGB_NONLINEAR_KHR;
    }
    state.swapchainImageFormat = surfaceFormat.format;

    uint32_t imageCount = caps.minImageCount + 1;
    if (caps.maxImageCount > 0 && imageCount > caps.maxImageCount) {
        imageCount = caps.maxImageCount;
    }
    state.swapchainImageCount = imageCount;

    VkSwapchainCreateInfoKHR scCreateInfo{};
    scCreateInfo.sType = VK_STRUCTURE_TYPE_SWAPCHAIN_CREATE_INFO_KHR;
    scCreateInfo.surface = surface;
    scCreateInfo.minImageCount = imageCount;
    scCreateInfo.imageFormat = surfaceFormat.format;
    scCreateInfo.imageColorSpace = surfaceFormat.colorSpace;
    scCreateInfo.imageExtent = state.swapchainExtent;
    scCreateInfo.imageArrayLayers = 1;
    scCreateInfo.imageUsage = VK_IMAGE_USAGE_COLOR_ATTACHMENT_BIT;
    scCreateInfo.imageSharingMode = VK_SHARING_MODE_EXCLUSIVE;
    scCreateInfo.preTransform = caps.currentTransform;
    scCreateInfo.compositeAlpha = VK_COMPOSITE_ALPHA_OPAQUE_BIT_KHR;
    scCreateInfo.presentMode = VK_PRESENT_MODE_FIFO_KHR;
    scCreateInfo.clipped = VK_TRUE;

    VkResult result = vkCreateSwapchainKHR(state.device, &scCreateInfo, nullptr, &state.swapchain);
    if (result != VK_SUCCESS) return result;

    vkGetSwapchainImagesKHR(state.device, state.swapchain, &imageCount, nullptr);
    state.swapchainImages.resize(imageCount);
    vkGetSwapchainImagesKHR(state.device, state.swapchain, &imageCount, state.swapchainImages.data());

    state.swapchainImageViews.resize(imageCount);
    for (size_t i = 0; i < imageCount; i++) {
        VkImageViewCreateInfo viewInfo{};
        viewInfo.sType = VK_STRUCTURE_TYPE_IMAGE_VIEW_CREATE_INFO;
        viewInfo.image = state.swapchainImages[i];
        viewInfo.viewType = VK_IMAGE_VIEW_TYPE_2D;
        viewInfo.format = state.swapchainImageFormat;
        viewInfo.subresourceRange.aspectMask = VK_IMAGE_ASPECT_COLOR_BIT;
        viewInfo.subresourceRange.baseMipLevel = 0;
        viewInfo.subresourceRange.levelCount = 1;
        viewInfo.subresourceRange.baseArrayLayer = 0;
        viewInfo.subresourceRange.layerCount = 1;
        vkCreateImageView(state.device, &viewInfo, nullptr, &state.swapchainImageViews[i]);
    }

    return VK_SUCCESS;
}

static VkResult CreateRenderPass(GlobalState& state) {
    VkAttachmentDescription colorAttachment{};
    colorAttachment.format = state.swapchainImageFormat;
    colorAttachment.samples = VK_SAMPLE_COUNT_1_BIT;
    colorAttachment.loadOp = VK_ATTACHMENT_LOAD_OP_CLEAR;
    colorAttachment.storeOp = VK_ATTACHMENT_STORE_OP_STORE;
    colorAttachment.stencilLoadOp = VK_ATTACHMENT_LOAD_OP_DONT_CARE;
    colorAttachment.stencilStoreOp = VK_ATTACHMENT_STORE_OP_DONT_CARE;
    colorAttachment.initialLayout = VK_IMAGE_LAYOUT_UNDEFINED;
    colorAttachment.finalLayout = VK_IMAGE_LAYOUT_PRESENT_SRC_KHR;

    VkAttachmentReference colorAttachmentRef{};
    colorAttachmentRef.attachment = 0;
    colorAttachmentRef.layout = VK_IMAGE_LAYOUT_COLOR_ATTACHMENT_OPTIMAL;

    VkSubpassDescription subpass{};
    subpass.pipelineBindPoint = VK_PIPELINE_BIND_POINT_GRAPHICS;
    subpass.colorAttachmentCount = 1;
    subpass.pColorAttachments = &colorAttachmentRef;

    VkRenderPassCreateInfo renderPassInfo{};
    renderPassInfo.sType = VK_STRUCTURE_TYPE_RENDER_PASS_CREATE_INFO;
    renderPassInfo.attachmentCount = 1;
    renderPassInfo.pAttachments = &colorAttachment;
    renderPassInfo.subpassCount = 1;
    renderPassInfo.pSubpasses = &subpass;

    return vkCreateRenderPass(state.device, &renderPassInfo, nullptr, &state.renderPass);
}

static VkResult CreateFramebuffers(GlobalState& state) {
    state.swapchainFramebuffers.resize(state.swapchainImageViews.size());
    for (size_t i = 0; i < state.swapchainImageViews.size(); i++) {
        VkImageView attachments[] = { state.swapchainImageViews[i] };
        VkFramebufferCreateInfo framebufferInfo{};
        framebufferInfo.sType = VK_STRUCTURE_TYPE_FRAMEBUFFER_CREATE_INFO;
        framebufferInfo.renderPass = state.renderPass;
        framebufferInfo.attachmentCount = 1;
        framebufferInfo.pAttachments = attachments;
        framebufferInfo.width = state.swapchainExtent.width;
        framebufferInfo.height = state.swapchainExtent.height;
        framebufferInfo.layers = 1;
        vkCreateFramebuffer(state.device, &framebufferInfo, nullptr, &state.swapchainFramebuffers[i]);
    }
    return VK_SUCCESS;
}

static VkResult CreateCommandPool(GlobalState& state) {
    VkCommandPoolCreateInfo poolInfo{};
    poolInfo.sType = VK_STRUCTURE_TYPE_COMMAND_POOL_CREATE_INFO;
    poolInfo.queueFamilyIndex = state.queueFamilyIndex;
    return vkCreateCommandPool(state.device, &poolInfo, nullptr, &state.commandPool);
}

static VkResult CreateCommandBuffers(GlobalState& state) {
    VkCommandBufferAllocateInfo allocInfo{};
    allocInfo.sType = VK_STRUCTURE_TYPE_COMMAND_BUFFER_ALLOCATE_INFO;
    allocInfo.commandPool = state.commandPool;
    allocInfo.level = VK_COMMAND_BUFFER_LEVEL_PRIMARY;
    allocInfo.commandBufferCount = 1;
    return vkAllocateCommandBuffers(state.device, &allocInfo, &state.commandBuffer);
}

static VkResult CreateSyncObjects(GlobalState& state) {
    VkSemaphoreCreateInfo semaphoreInfo{};
    semaphoreInfo.sType = VK_STRUCTURE_TYPE_SEMAPHORE_CREATE_INFO;
    VkFenceCreateInfo fenceInfo{};
    fenceInfo.sType = VK_STRUCTURE_TYPE_FENCE_CREATE_INFO;
    fenceInfo.flags = VK_FENCE_CREATE_SIGNALED_BIT;

    VkResult result = vkCreateSemaphore(state.device, &semaphoreInfo, nullptr, &state.imageAvailableSemaphore);
    if (result != VK_SUCCESS) return result;
    result = vkCreateSemaphore(state.device, &semaphoreInfo, nullptr, &state.renderFinishedSemaphore);
    if (result != VK_SUCCESS) return result;
    return vkCreateFence(state.device, &fenceInfo, nullptr, &state.inFlightFence);
}

static VkResult CreatePipelineLayout(GlobalState& state) {
    VkPipelineLayoutCreateInfo pipelineLayoutInfo{};
    pipelineLayoutInfo.sType = VK_STRUCTURE_TYPE_PIPELINE_LAYOUT_CREATE_INFO;
    pipelineLayoutInfo.setLayoutCount = 0;
    pipelineLayoutInfo.pSetLayouts = nullptr;
    pipelineLayoutInfo.pushConstantRangeCount = 0;
    pipelineLayoutInfo.pPushConstantRanges = nullptr;
    return vkCreatePipelineLayout(state.device, &pipelineLayoutInfo, nullptr, &state.pipelineLayout);
}

static VkResult CreateGraphicsPipeline(GlobalState& state) {
    VkPipelineVertexInputStateCreateInfo vertexInputInfo{};
    vertexInputInfo.sType = VK_STRUCTURE_TYPE_PIPELINE_VERTEX_INPUT_STATE_CREATE_INFO;
    vertexInputInfo.vertexBindingDescriptionCount = 0;
    vertexInputInfo.vertexAttributeDescriptionCount = 0;

    VkPipelineInputAssemblyStateCreateInfo inputAssembly{};
    inputAssembly.sType = VK_STRUCTURE_TYPE_PIPELINE_INPUT_ASSEMBLY_STATE_CREATE_INFO;
    inputAssembly.topology = VK_PRIMITIVE_TOPOLOGY_TRIANGLE_LIST;
    inputAssembly.primitiveRestartEnable = VK_FALSE;

    VkViewport viewport{};
    viewport.x = 0.0f;
    viewport.y = 0.0f;
    viewport.width = static_cast<float>(state.swapchainExtent.width);
    viewport.height = static_cast<float>(state.swapchainExtent.height);
    viewport.minDepth = 0.0f;
    viewport.maxDepth = 1.0f;

    VkRect2D scissor{};
    scissor.offset = {0, 0};
    scissor.extent = state.swapchainExtent;

    VkPipelineViewportStateCreateInfo viewportState{};
    viewportState.sType = VK_STRUCTURE_TYPE_PIPELINE_VIEWPORT_STATE_CREATE_INFO;
    viewportState.viewportCount = 1;
    viewportState.pViewports = &viewport;
    viewportState.scissorCount = 1;
    viewportState.pScissors = &scissor;

    VkPipelineRasterizationStateCreateInfo rasterizer{};
    rasterizer.sType = VK_STRUCTURE_TYPE_PIPELINE_RASTERIZATION_STATE_CREATE_INFO;
    rasterizer.depthClampEnable = VK_FALSE;
    rasterizer.rasterizerDiscardEnable = VK_FALSE;
    rasterizer.polygonMode = VK_POLYGON_MODE_FILL;
    rasterizer.lineWidth = 1.0f;
    rasterizer.cullMode = VK_CULL_MODE_BACK_BIT;
    rasterizer.frontFace = VK_FRONT_FACE_CLOCKWISE;
    rasterizer.depthBiasEnable = VK_FALSE;

    VkPipelineMultisampleStateCreateInfo multisampling{};
    multisampling.sType = VK_STRUCTURE_TYPE_PIPELINE_MULTISAMPLE_STATE_CREATE_INFO;
    multisampling.sampleShadingEnable = VK_FALSE;
    multisampling.rasterizationSamples = VK_SAMPLE_COUNT_1_BIT;

    VkPipelineColorBlendAttachmentState colorBlendAttachment{};
    colorBlendAttachment.colorWriteMask = VK_COLOR_COMPONENT_R_BIT | VK_COLOR_COMPONENT_G_BIT | VK_COLOR_COMPONENT_B_BIT | VK_COLOR_COMPONENT_A_BIT;
    colorBlendAttachment.blendEnable = VK_FALSE;

    VkPipelineColorBlendStateCreateInfo colorBlending{};
    colorBlending.sType = VK_STRUCTURE_TYPE_PIPELINE_COLOR_BLEND_STATE_CREATE_INFO;
    colorBlending.logicOpEnable = VK_FALSE;
    colorBlending.logicOp = VK_LOGIC_OP_COPY;
    colorBlending.attachmentCount = 1;
    colorBlending.pAttachments = &colorBlendAttachment;
    colorBlending.blendConstants[0] = 0.0f;
    colorBlending.blendConstants[1] = 0.0f;
    colorBlending.blendConstants[2] = 0.0f;
    colorBlending.blendConstants[3] = 0.0f;

    std::vector<VkPipelineShaderStageCreateInfo> shaderStages(2);
    shaderStages[0].sType = VK_STRUCTURE_TYPE_PIPELINE_SHADER_STAGE_CREATE_INFO;
    shaderStages[0].stage = VK_SHADER_STAGE_VERTEX_BIT;
    shaderStages[0].module = state.vertShaderModule;
    shaderStages[0].pName = "main";
    shaderStages[1].sType = VK_STRUCTURE_TYPE_PIPELINE_SHADER_STAGE_CREATE_INFO;
    shaderStages[1].stage = VK_SHADER_STAGE_FRAGMENT_BIT;
    shaderStages[1].module = state.fragShaderModule;
    shaderStages[1].pName = "main";

    VkGraphicsPipelineCreateInfo pipelineInfo{};
    pipelineInfo.sType = VK_STRUCTURE_TYPE_GRAPHICS_PIPELINE_CREATE_INFO;
    pipelineInfo.stageCount = static_cast<uint32_t>(shaderStages.size());
    pipelineInfo.pStages = shaderStages.data();
    pipelineInfo.pVertexInputState = &vertexInputInfo;
    pipelineInfo.pInputAssemblyState = &inputAssembly;
    pipelineInfo.pViewportState = &viewportState;
    pipelineInfo.pRasterizationState = &rasterizer;
    pipelineInfo.pMultisampleState = &multisampling;
    pipelineInfo.pDepthStencilState = nullptr;
    pipelineInfo.pColorBlendState = &colorBlending;
    pipelineInfo.pDynamicState = nullptr;
    pipelineInfo.layout = state.pipelineLayout;
    pipelineInfo.renderPass = state.renderPass;
    pipelineInfo.subpass = 0;
    pipelineInfo.basePipelineHandle = VK_NULL_HANDLE;

    return vkCreateGraphicsPipelines(state.device, state.pipelineCache, 1, &pipelineInfo, nullptr, &state.graphicsPipeline);
}

static VkResult InitVulkan(GlobalState& state, SDL_Window* window) {
    VkResult result;

    result = InitVulkanInstance(state);
    if (result != VK_SUCCESS) return result;

    result = PickPhysicalDevice(state);
    if (result != VK_SUCCESS) return result;

    result = CreateLogicalDevice(state);
    if (result != VK_SUCCESS) return result;

    // Create hardcoded shader modules
    state.vertShaderModule = CreateVulkanShaderModule(state,
        std::vector<uint32_t>(vert_spirv, vert_spirv + sizeof(vert_spirv) / sizeof(vert_spirv[0])));
    if (state.vertShaderModule == VK_NULL_HANDLE) return VK_ERROR_INITIALIZATION_FAILED;

    state.fragShaderModule = CreateVulkanShaderModule(state,
        std::vector<uint32_t>(frag_spirv, frag_spirv + sizeof(frag_spirv) / sizeof(frag_spirv[0])));
    if (state.fragShaderModule == VK_NULL_HANDLE) return VK_ERROR_INITIALIZATION_FAILED;

    result = CreateSwapchain(state, window);
    if (result != VK_SUCCESS) return result;

    result = CreateRenderPass(state);
    if (result != VK_SUCCESS) return result;

    result = CreateCommandPool(state);
    if (result != VK_SUCCESS) return result;

    result = CreateCommandBuffers(state);
    if (result != VK_SUCCESS) return result;

    result = CreateSyncObjects(state);
    if (result != VK_SUCCESS) return result;

    result = CreatePipelineLayout(state);
    if (result != VK_SUCCESS) return result;

    result = CreateGraphicsPipeline(state);
    if (result != VK_SUCCESS) return result;

    result = CreateFramebuffers(state);
    if (result != VK_SUCCESS) return result;

    state.initialized = true;
    APS5_LOG_OUT("[GNM] Vulkan backend initialized successfully\n", "");
    return VK_SUCCESS;
}

static void CleanupVulkan(GlobalState& state) {
    if (state.device != VK_NULL_HANDLE) {
        vkDeviceWaitIdle(state.device);
    }
    for (auto& framebuffer : state.swapchainFramebuffers) {
        if (framebuffer != VK_NULL_HANDLE) vkDestroyFramebuffer(state.device, framebuffer, nullptr);
    }
    if (state.graphicsPipeline != VK_NULL_HANDLE) vkDestroyPipeline(state.device, state.graphicsPipeline, nullptr);
    if (state.pipelineLayout != VK_NULL_HANDLE) vkDestroyPipelineLayout(state.device, state.pipelineLayout, nullptr);
    if (state.vertShaderModule != VK_NULL_HANDLE) vkDestroyShaderModule(state.device, state.vertShaderModule, nullptr);
    if (state.fragShaderModule != VK_NULL_HANDLE) vkDestroyShaderModule(state.device, state.fragShaderModule, nullptr);
    if (state.renderPass != VK_NULL_HANDLE) vkDestroyRenderPass(state.device, state.renderPass, nullptr);
    for (auto& imageView : state.swapchainImageViews) {
        if (imageView != VK_NULL_HANDLE) vkDestroyImageView(state.device, imageView, nullptr);
    }
    if (state.swapchain != VK_NULL_HANDLE) vkDestroySwapchainKHR(state.device, state.swapchain, nullptr);
    if (state.commandPool != VK_NULL_HANDLE) vkDestroyCommandPool(state.device, state.commandPool, nullptr);
    if (state.imageAvailableSemaphore != VK_NULL_HANDLE) vkDestroySemaphore(state.device, state.imageAvailableSemaphore, nullptr);
    if (state.renderFinishedSemaphore != VK_NULL_HANDLE) vkDestroySemaphore(state.device, state.renderFinishedSemaphore, nullptr);
    if (state.inFlightFence != VK_NULL_HANDLE) vkDestroyFence(state.device, state.inFlightFence, nullptr);
    if (state.device != VK_NULL_HANDLE) vkDestroyDevice(state.device, nullptr);
    if (state.instance != VK_NULL_HANDLE) vkDestroyInstance(state.instance, nullptr);
    state.initialized = false;
}

// ============================================================================
// GNM Command Buffer Decoder
// ============================================================================

// Forward declarations - definitions are earlier in this translation unit
Buffer* FindBufferByGpuAddr(uint64_t gpuAddr);
Texture* FindTextureByGpuAddr(uint64_t gpuAddr);

static void ExecuteCommandBuffer(GlobalState& state, const uint8_t* cmdData, uint64_t cmdSize) {
    uint64_t offset = 0;
    uint32_t cmdCount = 0;

    while (offset + sizeof(GnmCommand) <= cmdSize) {
        const GnmCommand* header = reinterpret_cast<const GnmCommand*>(cmdData + offset);
        offset += sizeof(GnmCommand);

        if (header->opcode == CMD_END_OF_BUFFER) {
            APS5_LOG_OUT("[GNM] Command buffer: end of buffer after %u commands\n", cmdCount);
            break;
        }

        if (offset + header->size > cmdSize) {
            APS5_LOG_OUT("[GNM] Command buffer: command 0x%X exceeds buffer bounds\n", header->opcode);
            break;
        }

        const uint8_t* cmdPayload = cmdData + offset;
        offset += header->size;
        cmdCount++;

        switch (header->opcode) {
        case CMD_NOP:
            break;

        case CMD_SET_SHADER_VS:
        case CMD_SET_SHADER_PS:
        case CMD_SET_SHADER_GS:
        case CMD_SET_SHADER_HS:
        case CMD_SET_SHADER_DS:
        case CMD_SET_SHADER_CS: {
            uint64_t shaderPtr = *reinterpret_cast<const uint64_t*>(cmdPayload);
            ShaderStage stage;
            switch (header->opcode) {
            case CMD_SET_SHADER_VS: stage = SHADER_STAGE_VS; break;
            case CMD_SET_SHADER_PS: stage = SHADER_STAGE_PS; break;
            case CMD_SET_SHADER_GS: stage = SHADER_STAGE_GS; break;
            case CMD_SET_SHADER_HS: stage = SHADER_STAGE_HS; break;
            case CMD_SET_SHADER_DS: stage = SHADER_STAGE_DS; break;
            case CMD_SET_SHADER_CS: stage = SHADER_STAGE_CS; break;
            default: stage = SHADER_STAGE_VS; break;
            }
            APS5_LOG_OUT("[GNM] CMD: SetShader stage=%u ptr=0x%llX\n", stage, (unsigned long long)shaderPtr);
            break;
        }

        case CMD_SET_VIEWPORT: {
            if (header->size < sizeof(SetViewportCmd)) break;
            const SetViewportCmd* cmd = reinterpret_cast<const SetViewportCmd*>(cmdPayload);
            state.drawContext.viewportWidth = static_cast<uint32_t>(cmd->width);
            state.drawContext.viewportHeight = static_cast<uint32_t>(cmd->height);
            VkViewport viewport{};
            viewport.x = cmd->x;
            viewport.y = cmd->y;
            viewport.width = cmd->width;
            viewport.height = cmd->height;
            viewport.minDepth = cmd->minDepth;
            viewport.maxDepth = cmd->maxDepth;
            vkCmdSetViewport(state.commandBuffer, 0, 1, &viewport);
            APS5_LOG_OUT("[GNM] CMD: SetViewport %f,%f %fx%f\n", cmd->x, cmd->y, cmd->width, cmd->height);
            break;
        }

        case CMD_SET_SCISSOR: {
            if (header->size < sizeof(SetScissorCmd)) break;
            const SetScissorCmd* cmd = reinterpret_cast<const SetScissorCmd*>(cmdPayload);
            state.drawContext.scissorWidth = cmd->width;
            state.drawContext.scissorHeight = cmd->height;
            VkRect2D scissor{};
            scissor.offset = {static_cast<int32_t>(cmd->x), static_cast<int32_t>(cmd->y)};
            scissor.extent = {cmd->width, cmd->height};
            vkCmdSetScissor(state.commandBuffer, 0, 1, &scissor);
            APS5_LOG_OUT("[GNM] CMD: SetScissor %u,%u %ux%u\n", cmd->x, cmd->y, cmd->width, cmd->height);
            break;
        }

        case CMD_SET_PRIMITIVE_TYPE: {
            if (header->size < sizeof(SetPrimitiveTypeCmd)) break;
            const SetPrimitiveTypeCmd* cmd = reinterpret_cast<const SetPrimitiveTypeCmd*>(cmdPayload);
            state.drawContext.primitiveType = static_cast<PrimitiveType>(cmd->primitiveType);
            APS5_LOG_OUT("[GNM] CMD: SetPrimitiveType %u\n", cmd->primitiveType);
            break;
        }

        case CMD_DRAW: {
            if (header->size < sizeof(DrawCmd)) break;
            const DrawCmd* cmd = reinterpret_cast<const DrawCmd*>(cmdPayload);
            APS5_LOG_OUT("[GNM] CMD: Draw vertices=%u instances=%u firstVertex=%u firstInstance=%u\n",
                         cmd->vertexCount, cmd->instanceCount, cmd->firstVertex, cmd->firstInstance);
            vkCmdDraw(state.commandBuffer, cmd->vertexCount, cmd->instanceCount,
                       cmd->firstVertex, cmd->firstInstance);
            break;
        }

        case CMD_DRAW_INDEXED: {
            if (header->size < sizeof(DrawIndexedCmd)) break;
            const DrawIndexedCmd* cmd = reinterpret_cast<const DrawIndexedCmd*>(cmdPayload);
            APS5_LOG_OUT("[GNM] CMD: DrawIndexed indices=%u instances=%u firstIndex=%u vertexOffset=%d firstInstance=%u\n",
                         cmd->indexCount, cmd->instanceCount, cmd->firstIndex, cmd->vertexOffset, cmd->firstInstance);
            vkCmdDrawIndexed(state.commandBuffer, cmd->indexCount, cmd->instanceCount,
                              cmd->firstIndex, cmd->vertexOffset, cmd->firstInstance);
            break;
        }

        case CMD_DISPATCH: {
            if (header->size < sizeof(DispatchCmd)) break;
            const DispatchCmd* cmd = reinterpret_cast<const DispatchCmd*>(cmdPayload);
            APS5_LOG_OUT("[GNM] CMD: Dispatch %ux%ux%u\n", cmd->threadGroupX, cmd->threadGroupY, cmd->threadGroupZ);
            break;
        }

        case CMD_SET_VERTEX_BUFFER: {
            if (header->size < sizeof(SetVertexBufferCmd)) break;
            const SetVertexBufferCmd* cmd = reinterpret_cast<const SetVertexBufferCmd*>(cmdPayload);
            Buffer* buf = FindBufferByGpuAddr(cmd->gpuAddress);
            if (buf && buf->vk.buffer != VK_NULL_HANDLE) {
                VkDeviceSize offset = 0;
                vkCmdBindVertexBuffers(state.commandBuffer, cmd->slot, 1, &buf->vk.buffer, &offset);
                APS5_LOG_OUT("[GNM] CMD: SetVertexBuffer slot=%u bound VK buffer\n", cmd->slot);
            } else {
                APS5_LOG_OUT("[GNM] CMD: SetVertexBuffer slot=%u addr=0x%llX - buffer not found\n",
                             cmd->slot, (unsigned long long)cmd->gpuAddress);
            }
            break;
        }

        case CMD_SET_INDEX_BUFFER: {
            if (header->size < sizeof(SetIndexBufferCmd)) break;
            const SetIndexBufferCmd* cmd = reinterpret_cast<const SetIndexBufferCmd*>(cmdPayload);
            Buffer* buf = FindBufferByGpuAddr(cmd->gpuAddress);
            if (buf && buf->vk.buffer != VK_NULL_HANDLE) {
                VkIndexType idxType = (cmd->format == 0) ? VK_INDEX_TYPE_UINT16 : VK_INDEX_TYPE_UINT32;
                vkCmdBindIndexBuffer(state.commandBuffer, buf->vk.buffer, 0, idxType);
                APS5_LOG_OUT("[GNM] CMD: SetIndexBuffer bound VK buffer, format=%u\n", cmd->format);
            } else {
                APS5_LOG_OUT("[GNM] CMD: SetIndexBuffer addr=0x%llX - buffer not found\n",
                             (unsigned long long)cmd->gpuAddress);
            }
            break;
        }

        case CMD_SET_CONSTANT_BUFFER: {
            if (header->size < sizeof(SetConstantBufferCmd)) break;
            const SetConstantBufferCmd* cmd = reinterpret_cast<const SetConstantBufferCmd*>(cmdPayload);
            Buffer* buf = FindBufferByGpuAddr(cmd->gpuAddress);
            if (buf && buf->vk.buffer != VK_NULL_HANDLE) {
                APS5_LOG_OUT("[GNM] CMD: SetConstantBuffer slot=%u bound VK buffer\n", cmd->slot);
            } else {
                APS5_LOG_OUT("[GNM] CMD: SetConstantBuffer slot=%u addr=0x%llX - buffer not found\n",
                             cmd->slot, (unsigned long long)cmd->gpuAddress);
            }
            break;
        }

        case CMD_SET_TEXTURE: {
            if (header->size < sizeof(SetTextureCmd)) break;
            const SetTextureCmd* cmd = reinterpret_cast<const SetTextureCmd*>(cmdPayload);
            Texture* tex = FindTextureByGpuAddr(cmd->gpuAddress);
            if (tex && tex->vk.view != VK_NULL_HANDLE) {
                APS5_LOG_OUT("[GNM] CMD: SetTexture slot=%u bound VK image view\n", cmd->slot);
            } else {
                APS5_LOG_OUT("[GNM] CMD: SetTexture slot=%u addr=0x%llX - texture not found\n",
                             cmd->slot, (unsigned long long)cmd->gpuAddress);
            }
            break;
        }

        case CMD_SET_SAMPLER: {
            if (header->size < sizeof(SetSamplerCmd)) break;
            const SetSamplerCmd* cmd = reinterpret_cast<const SetSamplerCmd*>(cmdPayload);
            APS5_LOG_OUT("[GNM] CMD: SetSampler slot=%u filter=%u addrU=%u addrV=%u addrW=%u\n",
                         cmd->slot, cmd->filterMode, cmd->addressU, cmd->addressV, cmd->addressW);
            break;
        }

        case CMD_SET_RENDER_TARGET: {
            if (header->size < sizeof(SetRenderTargetCmd)) break;
            const SetRenderTargetCmd* cmd = reinterpret_cast<const SetRenderTargetCmd*>(cmdPayload);
            Texture* tex = FindTextureByGpuAddr(cmd->gpuAddress);
            if (tex) {
                state.drawContext.renderTarget.width = cmd->width;
                state.drawContext.renderTarget.height = cmd->height;
                state.drawContext.renderTarget.format = cmd->format;
                APS5_LOG_OUT("[GNM] CMD: SetRenderTarget slot=%u %ux%u fmt=%u\n",
                             cmd->slot, cmd->width, cmd->height, cmd->format);
            } else {
                APS5_LOG_OUT("[GNM] CMD: SetRenderTarget slot=%u addr=0x%llX - texture not found\n",
                             cmd->slot, (unsigned long long)cmd->gpuAddress);
            }
            break;
        }

        default:
            APS5_LOG_OUT("[GNM] CMD: Unknown opcode 0x%X (size=%u)\n", header->opcode, header->size);
            break;
        }
    }

    if (cmdCount > 0) {
        APS5_LOG_OUT("[GNM] Command buffer: executed %u commands\n", cmdCount);
    }
}

// ============================================================================
// Shader compilation: GCN to SPIR-V to Vulkan shader module
// ============================================================================

static VkShaderModule CreateVulkanShaderModule(GlobalState& state, const std::vector<uint32_t>& spirv) {
    VkShaderModuleCreateInfo createInfo{};
    createInfo.sType = VK_STRUCTURE_TYPE_SHADER_MODULE_CREATE_INFO;
    createInfo.codeSize = spirv.size() * sizeof(uint32_t);
    createInfo.pCode = spirv.data();

    VkShaderModule module = VK_NULL_HANDLE;
    VkResult result = vkCreateShaderModule(state.device, &createInfo, nullptr, &module);
    if (result != VK_SUCCESS) {
        APS5_LOG_OUT("[GNM] Failed to create Vulkan shader module\n", "");
        return VK_NULL_HANDLE;
    }
    return module;
}

static void CompileAndStoreShader(GlobalState& state, Shader* shader) {
    if (!shader || shader->bytecode.empty()) return;

    // Use shader recompiler to convert GCN to SPIR-V
    ShaderRecompiler::ShaderBinary shaderBinary{};
    shaderBinary.stage = ShaderRecompiler::ShaderStage::Vertex;  // Default, should be set per shader type
    shaderBinary.codeAddress = 0;
    shaderBinary.code = {};
    shaderBinary.headerAddress = 0;
    shaderBinary.header = {};

    // For now, store the raw bytecode; full GCN->SPIR-V compilation requires
    // a complete RecompileRequest with descriptor bindings, vertex attributes, etc.
    // This will be expanded as the shader decoder matures.
    APS5_LOG_OUT("[GNM] Shader bytecode stored: %u bytes\n", shader->bytecode.size());
}

} // namespace Gnm
} // namespace sce