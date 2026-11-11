#include "prx/libSceGnm/include/Gnm.hpp"
#include "prx/libc/include/General.hpp"

namespace sce {
namespace Gnm {

GlobalState& GetGlobalState() {
    static GlobalState state;
    return state;
}

} // namespace Gnm
} // namespace sce