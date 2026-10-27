#include <nid/NidResolver.hpp>
#include <nid/ExportExclusions.hpp>
#include <nid/NidCompute.hpp>
#include <nid/NidPatcherUtils.hpp>
#include <cstdint>
#include <stdexcept>
#include <unordered_set>
#include <vector>

namespace Nid {

std::string ResolveOneName(const std::string& funcName) {
    using namespace Internal;

    if (IsNidNoPatchCut(funcName))
        return StripNidNoPatchCut(funcName);
    if (IsNidNoPatch(funcName))
        return funcName;

    return ComputeNid(StripNidPostfix(funcName), "");
}

std::unordered_map<std::string, std::string> ResolveNids(const std::vector<std::string>& exportedNames, const std::string& libraryName, const std::unordered_set<std::string>& excludedExports) {
    using namespace Internal;

    std::unordered_set<std::string> nameSet(exportedNames.begin(), exportedNames.end());

    if (nameSet.size() != exportedNames.size()) {
        for (std::size_t i = 0u; i < exportedNames.size(); ++i) {
            for (std::size_t j = i + 1u; j < exportedNames.size(); ++j) {
                if (exportedNames[i] == exportedNames[j])
                    throw std::runtime_error("duplicate exported symbol \"" + exportedNames[i] + "\" in library \"" + libraryName + "\"");
            }
        }
    }

    std::unordered_map<std::string, std::string> result;
    result.reserve(exportedNames.size());
    std::unordered_set<std::string> assignedNids;
    assignedNids.reserve(exportedNames.size());

    for (const std::string& name : exportedNames) {
        std::string assigned;
        if (excludedExports.contains(NormalizeExportName(name))) {
            assigned = name;
        } else if (IsNidNoPatchCut(name)) {
            assigned = StripNidNoPatchCut(name);
        } else if (IsNidNoPatch(name)) {
            assigned = name;
        } else {
            const std::string stripped = StripNidPostfix(name);
            const bool hasPostfix = stripped != name;

            if (!hasPostfix && nameSet.count(name + kNidPostfix)) {
                assigned = name;
            } else {
                assigned = ComputeNid(stripped, libraryName);
            }
        }

        if (assignedNids.contains(assigned)) {
            result[name] = name;
            assignedNids.insert(name);
        } else {
            result[name] = assigned;
            assignedNids.insert(assigned);
        }
    }

    return result;
}

}
