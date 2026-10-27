import ghidra.app.script.GhidraScript;
import ghidra.program.model.reloc.*;
import ghidra.program.model.symbol.*;
import ghidra.program.model.address.*;
import java.util.Iterator;

public class DumpCallSites extends GhidraScript {
    @Override
    public void run() throws Exception {
        for (long addr : new long[]{0x01c83260L, 0x01c83268L}) {
            Address a = toAddr(addr);
            println("Address: " + a);
            Symbol s = getSymbolAt(a);
            println("  Symbol: " + (s != null ? s.getName() : "none"));
            
            RelocationTable relocs = currentProgram.getRelocationTable();
            Iterator<Relocation> it = relocs.getRelocations(new AddressSet(toAddr(addr - 16), toAddr(addr + 16)));
            while (it.hasNext()) {
                Relocation rel = it.next();
                println("    Reloc at " + rel.getAddress() + " -> " + rel.getSymbolName());
            }
        }
    }
}
