#include "prx/libSceGnm/include/Gnm.hpp"
#include "prx/libc/include/General.hpp"
#include "prx/libc/include/GuestArena.hpp"
#include "prx/libSceVideoOut/include/VideoOutWindow.hpp"

#include <unordered_map>

namespace sce { namespace Gnm {

// Resource management: map PS4 GPU addresses to Vulkan resources
static std::unordered_map<uint64_t, Buffer*>   g_bufferMap;
static std::unordered_map<uint64_t, Texture*>  g_textureMap;
static std::unordered_map<uint64_t, Shader*>   g_shaderMap;
static std::unordered_map<uint64_t, Sampler*>  g_samplerMap;

Buffer* FindBufferByGpuAddr(uint64_t gpuAddr) {
    auto it = g_bufferMap.find(gpuAddr);
    return it != g_bufferMap.end() ? it->second : nullptr;
}
Texture* FindTextureByGpuAddr(uint64_t gpuAddr) {
    auto it = g_textureMap.find(gpuAddr);
    return it != g_textureMap.end() ? it->second : nullptr;
}
Shader* FindShaderByGpuAddr(uint64_t gpuAddr) {
    auto it = g_shaderMap.find(gpuAddr);
    return it != g_shaderMap.end() ? it->second : nullptr;
}
void RegisterBuffer(Buffer* buf) {
    if (buf && buf->gpuAddress != 0) g_bufferMap[buf->gpuAddress] = buf;
}
void RegisterTexture(Texture* tex) {
    if (tex && tex->gpuAddress != 0) g_textureMap[tex->gpuAddress] = tex;
}
void RegisterShader(Shader* sh) {
    if (sh && sh->shaderPtr) g_shaderMap[reinterpret_cast<uint64_t>(sh->shaderPtr)] = sh;
}

// Read guest memory at a GPU address using GuestArena
static const uint8_t* ReadGuestMemory(uint64_t gpuAddr, uint64_t size) {
    // Use GuestArenaResidentSpan to get a host-accessible pointer for guest memory
    std::uintptr_t start = 0, end = 0;
    if (!GuestArena::GuestArenaResidentSpan_nid_postfix(static_cast<std::uintptr_t>(gpuAddr), size, &start, &end)) {
        APS5_LOG_OUT("[GNM] GuestArenaResidentSpan failed for addr=0x%llX size=%llu\n",
                     (unsigned long long)gpuAddr, (unsigned long long)size);
        return nullptr;
    }
    return reinterpret_cast<const uint8_t*>(start);
}

}} // namespace sce::Gnm

#include "prx/libSceGnm/src/GnmVulkan.cpp"

extern "C" {

APS5_EXPORT("xbxNatawohc", sceGnmSubmitAndFlipCommandBuffers_stub);
APS5_EXPORT("1qXLHIpROPE", sceGnmInsertWaitFlipDone_stub);
APS5_EXPORT("gAhCn6UiU4Y", sceGnmSetVsShader_stub);
APS5_EXPORT("5uFKckiJYRM", sceGnmSetPsShader350_stub);
APS5_EXPORT("UJwNuMBcUAk", sceGnmSetGsShader_stub);
APS5_EXPORT("VJNjFtqiF5w", sceGnmSetHsShader_stub);
APS5_EXPORT("nvEwfYAImTs", sceGnmRegisterResource_stub);
APS5_EXPORT("HlTPoZ-oY7Y", sceGnmDrawIndex_stub);
APS5_EXPORT("GGsn7jMTxw4", sceGnmDrawIndexAuto_stub);
APS5_EXPORT("zwY0YV91TTI", sceGnmSubmitCommandBuffers_stub);
APS5_EXPORT("b0xyllnVY-I", sceGnmAddEqEvent_stub);
APS5_EXPORT("yb2cRhagD1I", sceGnmDrawInitDefaultHardwareState350_stub);
APS5_EXPORT("yvZ73uQUqrk", sceGnmSubmitDone_stub);
APS5_EXPORT("V31V01UiScY", sceGnmUpdateVsShader_stub);
APS5_EXPORT("mLVL7N7BVBg", sceGnmUpdatePsShader350_stub);

static sce::Gnm::GlobalState& gnmState() {
    return sce::Gnm::GetGlobalState();
}

int APS5_VABI sceGnmSubmitAndFlipCommandBuffers_stub(void) {
    auto& state = gnmState();
    if (!state.initialized) {
        SDL_Window* window = GetVideoOutSDLWindow();
        if (!window) {
            APS5_LOG_OUT("[GNM] No SDL window available for Vulkan init\n", "");
            return 0;
        }
        VkResult result = InitVulkan(state, window);
        if (result != VK_SUCCESS) {
            APS5_LOG_OUT("[GNM] Vulkan init failed\n", "");
            return 0;
        }
    }

    vkWaitForFences(state.device, 1, &state.inFlightFence, VK_TRUE, UINT64_MAX);
    vkResetFences(state.device, 1, &state.inFlightFence);

    uint32_t imageIndex;
    VkResult result = vkAcquireNextImageKHR(state.device, state.swapchain, UINT64_MAX,
                                             state.imageAvailableSemaphore, VK_NULL_HANDLE, &imageIndex);
    if (result == VK_ERROR_OUT_OF_DATE_KHR) {
        return 0;
    }

    VkCommandBufferBeginInfo beginInfo{};
    beginInfo.sType = VK_STRUCTURE_TYPE_COMMAND_BUFFER_BEGIN_INFO;
    beginInfo.flags = VK_COMMAND_BUFFER_USAGE_ONE_TIME_SUBMIT_BIT;
    vkBeginCommandBuffer(state.commandBuffer, &beginInfo);

    VkRenderPassBeginInfo renderPassInfo{};
    renderPassInfo.sType = VK_STRUCTURE_TYPE_RENDER_PASS_BEGIN_INFO;
    renderPassInfo.renderPass = state.renderPass;
    renderPassInfo.framebuffer = state.swapchainFramebuffers[imageIndex];
    renderPassInfo.renderArea.offset = {0, 0};
    renderPassInfo.renderArea.extent = state.swapchainExtent;
    VkClearValue clearColor = {{{0.1f, 0.1f, 0.1f, 1.0f}}};
    renderPassInfo.clearValueCount = 1;
    renderPassInfo.pClearValues = &clearColor;

    vkCmdBeginRenderPass(state.commandBuffer, &renderPassInfo, VK_SUBPASS_CONTENTS_INLINE);
    vkCmdBindPipeline(state.commandBuffer, VK_PIPELINE_BIND_POINT_GRAPHICS, state.graphicsPipeline);

    // Execute GNM command buffer - translates PS4 commands to Vulkan calls
    if (state.currentCommandBuffer.cpuAddress && state.currentCommandBuffer.size > 0) {
        APS5_LOG_OUT("[GNM] Executing command buffer: cpuAddress=%p size=%llu\n",
                     state.currentCommandBuffer.cpuAddress,
                     (unsigned long long)state.currentCommandBuffer.size);
        ExecuteCommandBuffer(state, static_cast<const uint8_t*>(state.currentCommandBuffer.cpuAddress),
                              state.currentCommandBuffer.size);
    } else if (state.currentCommandBuffer.gpuAddress != 0 && state.currentCommandBuffer.size > 0) {
        APS5_LOG_OUT("[GNM] Reading command buffer from GPU addr=0x%llX size=%llu\n",
                     (unsigned long long)state.currentCommandBuffer.gpuAddress,
                     (unsigned long long)state.currentCommandBuffer.size);
        const uint8_t* cmdData = sce::Gnm::ReadGuestMemory(state.currentCommandBuffer.gpuAddress,
                                                  state.currentCommandBuffer.size);
        if (cmdData) {
            ExecuteCommandBuffer(state, cmdData, state.currentCommandBuffer.size);
        } else {
            APS5_LOG_OUT("[GNM] Failed to read command buffer from GPU memory\n", "");
        }
    } else {
        APS5_LOG_OUT("[GNM] No command buffer data (cpuAddress=%p, gpuAddress=0x%llX, size=%llu)\n",
                     state.currentCommandBuffer.cpuAddress,
                     (unsigned long long)state.currentCommandBuffer.gpuAddress,
                     (unsigned long long)state.currentCommandBuffer.size);
        // Fallback: draw a hardcoded triangle to verify pipeline works
        VkViewport viewport{};
        viewport.x = 0.0f;
        viewport.y = 0.0f;
        viewport.width = static_cast<float>(state.swapchainExtent.width);
        viewport.height = static_cast<float>(state.swapchainExtent.height);
        viewport.minDepth = 0.0f;
        viewport.maxDepth = 1.0f;
        vkCmdSetViewport(state.commandBuffer, 0, 1, &viewport);

        VkRect2D scissor{};
        scissor.offset = {0, 0};
        scissor.extent = state.swapchainExtent;
        vkCmdSetScissor(state.commandBuffer, 0, 1, &scissor);

        // Draw hardcoded triangle
        vkCmdDraw(state.commandBuffer, 3, 1, 0, 0);
    }

    vkCmdEndRenderPass(state.commandBuffer);
    vkEndCommandBuffer(state.commandBuffer);

    VkSubmitInfo submitInfo{};
    submitInfo.sType = VK_STRUCTURE_TYPE_SUBMIT_INFO;
    submitInfo.waitSemaphoreCount = 1;
    submitInfo.pWaitSemaphores = &state.imageAvailableSemaphore;
    VkPipelineStageFlags waitStages[] = {VK_PIPELINE_STAGE_COLOR_ATTACHMENT_OUTPUT_BIT};
    submitInfo.pWaitDstStageMask = waitStages;
    submitInfo.commandBufferCount = 1;
    submitInfo.pCommandBuffers = &state.commandBuffer;
    submitInfo.signalSemaphoreCount = 1;
    submitInfo.pSignalSemaphores = &state.renderFinishedSemaphore;

    result = vkQueueSubmit(state.queue, 1, &submitInfo, state.inFlightFence);
    if (result != VK_SUCCESS) {
        APS5_LOG_OUT("[GNM] Queue submit failed\n", "");
        return -1;
    }

    VkPresentInfoKHR presentInfo{};
    presentInfo.sType = VK_STRUCTURE_TYPE_PRESENT_INFO_KHR;
    presentInfo.waitSemaphoreCount = 1;
    presentInfo.pWaitSemaphores = &state.renderFinishedSemaphore;
    presentInfo.swapchainCount = 1;
    presentInfo.pSwapchains = &state.swapchain;
    presentInfo.pImageIndices = &imageIndex;
    presentInfo.pResults = nullptr;

    result = vkQueuePresentKHR(state.queue, &presentInfo);
    if (result == VK_ERROR_OUT_OF_DATE_KHR || result == VK_SUBOPTIMAL_KHR) {
        // Swapchain needs recreation
    } else if (result != VK_SUCCESS) {
        APS5_LOG_OUT("[GNM] Present failed\n", "");
    }

    state.frameIndex++;
    state.flipPending = false;

    APS5_LOG_OUT("[GNM] SubmitAndFlip: frame %u presented\n", state.frameIndex);
    return 0;
}

int APS5_VABI sceGnmInsertWaitFlipDone_stub(void) {
    auto& state = gnmState();
    if (!state.initialized) return 0;

    VkResult result = vkWaitForFences(state.device, 1, &state.inFlightFence, VK_TRUE, UINT64_MAX);
    if (result == VK_SUCCESS) {
        vkResetFences(state.device, 1, &state.inFlightFence);
        state.flipPending = false;
    }
    return 0;
}

int APS5_VABI sceGnmSetVsShader_stub(void* vsShaderPtr) {
    auto& state = gnmState();
    if (!state.initialized) return 0;
    sce::Gnm::Shader* shader = sce::Gnm::FindShaderByGpuAddr(reinterpret_cast<uint64_t>(vsShaderPtr));
    if (!shader) {
        shader = new sce::Gnm::Shader();
        shader->shaderPtr = vsShaderPtr;
        shader->stage = sce::Gnm::SHADER_STAGE_VS;
        sce::Gnm::RegisterShader(shader);
    }
    state.drawContext.vsShader = shader;
    sce::Gnm::CompileAndStoreShader(state, shader);
    APS5_LOG_OUT("[GNM] SetVsShader: ptr=%p\n", vsShaderPtr);
    return 0;
}

int APS5_VABI sceGnmSetPsShader350_stub(void* psShaderPtr) {
    auto& state = gnmState();
    if (!state.initialized) return 0;
    sce::Gnm::Shader* shader = sce::Gnm::FindShaderByGpuAddr(reinterpret_cast<uint64_t>(psShaderPtr));
    if (!shader) {
        shader = new sce::Gnm::Shader();
        shader->shaderPtr = psShaderPtr;
        shader->stage = sce::Gnm::SHADER_STAGE_PS;
        sce::Gnm::RegisterShader(shader);
    }
    state.drawContext.psShader = shader;
    sce::Gnm::CompileAndStoreShader(state, shader);
    APS5_LOG_OUT("[GNM] SetPsShader350: ptr=%p\n", psShaderPtr);
    return 0;
}

int APS5_VABI sceGnmSetGsShader_stub(void* gsShaderPtr) {
    auto& state = gnmState();
    if (!state.initialized) return 0;
    sce::Gnm::Shader* shader = sce::Gnm::FindShaderByGpuAddr(reinterpret_cast<uint64_t>(gsShaderPtr));
    if (!shader) {
        shader = new sce::Gnm::Shader();
        shader->shaderPtr = gsShaderPtr;
        shader->stage = sce::Gnm::SHADER_STAGE_GS;
        sce::Gnm::RegisterShader(shader);
    }
    state.drawContext.gsShader = shader;
    sce::Gnm::CompileAndStoreShader(state, shader);
    APS5_LOG_OUT("[GNM] SetGsShader: ptr=%p\n", gsShaderPtr);
    return 0;
}

int APS5_VABI sceGnmSetHsShader_stub(void* hsShaderPtr) {
    auto& state = gnmState();
    if (!state.initialized) return 0;
    sce::Gnm::Shader* shader = sce::Gnm::FindShaderByGpuAddr(reinterpret_cast<uint64_t>(hsShaderPtr));
    if (!shader) {
        shader = new sce::Gnm::Shader();
        shader->shaderPtr = hsShaderPtr;
        shader->stage = sce::Gnm::SHADER_STAGE_HS;
        sce::Gnm::RegisterShader(shader);
    }
    state.drawContext.hsShader = shader;
    sce::Gnm::CompileAndStoreShader(state, shader);
    APS5_LOG_OUT("[GNM] SetHsShader: ptr=%p\n", hsShaderPtr);
    return 0;
}

int APS5_VABI sceGnmRegisterResource_stub(void* resourcePtr, uint32_t resourceType, uint64_t gpuAddress, uint64_t size) {
    auto& state = gnmState();
    if (!state.initialized) return 0;
    if (resourceType == 0) {
        sce::Gnm::Buffer* buf = sce::Gnm::FindBufferByGpuAddr(gpuAddress);
        if (!buf) {
            buf = new sce::Gnm::Buffer();
            buf->gpuAddress = gpuAddress;
            buf->size = size;
            buf->type = static_cast<sce::Gnm::BufferType>(resourceType);
            buf->cpuAddress = resourcePtr;
            sce::Gnm::RegisterBuffer(buf);
        }
        APS5_LOG_OUT("[GNM] RegisterResource: buffer addr=0x%llX size=%llu type=%u\n",
                     (unsigned long long)gpuAddress, (unsigned long long)size, resourceType);
    } else if (resourceType == 1) {
        sce::Gnm::Texture* tex = sce::Gnm::FindTextureByGpuAddr(gpuAddress);
        if (!tex) {
            tex = new sce::Gnm::Texture();
            tex->gpuAddress = gpuAddress;
            tex->size = size;
            tex->type = static_cast<sce::Gnm::ResourceType>(resourceType);
            tex->cpuAddress = resourcePtr;
            sce::Gnm::RegisterTexture(tex);
        }
        APS5_LOG_OUT("[GNM] RegisterResource: texture addr=0x%llX size=%llu type=%u\n",
                     (unsigned long long)gpuAddress, (unsigned long long)size, resourceType);
    }
    return 0;
}

int APS5_VABI sceGnmDrawIndex_stub(uint32_t indexCount, uint32_t startIndex, uint32_t primCount) {
    auto& state = gnmState();
    if (!state.initialized) return 0;
    APS5_LOG_OUT("[GNM] DrawIndex: count=%u start=%u prims=%u\n",
                 indexCount, startIndex, primCount);
    return 0;
}

int APS5_VABI sceGnmDrawIndexAuto_stub(uint32_t indexCount) {
    auto& state = gnmState();
    if (!state.initialized) return 0;
    APS5_LOG_OUT("[GNM] DrawIndexAuto: count=%u\n", indexCount);
    return 0;
}

int APS5_VABI sceGnmSubmitCommandBuffers_stub(void* cmdBuffers, uint32_t numBuffers) {
    auto& state = gnmState();
    if (!state.initialized) return 0;
    APS5_LOG_OUT("[GNM] SubmitCommandBuffers: numBuffers=%u\n", numBuffers);
    return 0;
}

int APS5_VABI sceGnmAddEqEvent_stub(void) {
    auto& state = gnmState();
    if (!state.initialized) return 0;
    APS5_LOG_OUT("[GNM] AddEqEvent\n", "");
    return 0;
}

int APS5_VABI sceGnmSubmitDone_stub(void) {
    auto& state = gnmState();
    if (!state.initialized) return 0;
    APS5_LOG_OUT("[GNM] SubmitDone\n", "");
    return 0;
}

int APS5_VABI sceGnmDrawInitDefaultHardwareState350_stub(void) {
    auto& state = gnmState();
    if (!state.initialized) return 0;
    APS5_LOG_OUT("[GNM] DrawInitDefaultHardwareState350\n", "");
    return 0;
}

int APS5_VABI sceGnmUpdateVsShader_stub(void* vsShaderPtr) {
    auto& state = gnmState();
    if (!state.initialized) return 0;
    sce::Gnm::Shader* shader = sce::Gnm::FindShaderByGpuAddr(reinterpret_cast<uint64_t>(vsShaderPtr));
    if (!shader) {
        shader = new sce::Gnm::Shader();
        shader->shaderPtr = vsShaderPtr;
        shader->stage = sce::Gnm::SHADER_STAGE_VS;
        sce::Gnm::RegisterShader(shader);
    }
    state.drawContext.vsShader = shader;
    sce::Gnm::CompileAndStoreShader(state, shader);
    APS5_LOG_OUT("[GNM] UpdateVsShader: ptr=%p\n", vsShaderPtr);
    return 0;
}

int APS5_VABI sceGnmUpdatePsShader350_stub(void* psShaderPtr) {
    auto& state = gnmState();
    if (!state.initialized) return 0;
    sce::Gnm::Shader* shader = sce::Gnm::FindShaderByGpuAddr(reinterpret_cast<uint64_t>(psShaderPtr));
    if (!shader) {
        shader = new sce::Gnm::Shader();
        shader->shaderPtr = psShaderPtr;
        shader->stage = sce::Gnm::SHADER_STAGE_PS;
        sce::Gnm::RegisterShader(shader);
    }
    state.drawContext.psShader = shader;
    sce::Gnm::CompileAndStoreShader(state, shader);
    APS5_LOG_OUT("[GNM] UpdatePsShader350: ptr=%p\n", psShaderPtr);
    return 0;
}

} // extern "C"