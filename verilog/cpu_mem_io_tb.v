`timescale 1ns/1ps

module cpu_mem_io_tb;

reg clk;
reg reset;

reg [3:0] KEY;
reg [9:0] SW;

wire [9:0] LEDR;

cpu uut(
    .clk(clk),
    .reset(reset),
    .KEY(KEY),
    .SW(SW),
    .LEDR(LEDR)
);

// clock
always #5 clk = ~clk;

initial begin
    clk = 0;
    reset = 1;

    KEY = 4'b0000;
    SW  = 10'b1010101010; // test input

    // LW R1,0(R2)   ; R1 = SW
    // SW R1,0(R3)   ; LEDR = R1

    uut.imem[16] = 32'h12000004; // LW R1,0(R2)
    uut.imem[17] = 32'h31000005; // SW R1,0(R3)

    #10;
    reset = 0;

    #1;

    uut.rf0.regs[2] = 32'hF0000014; // SW input address
    uut.rf0.regs[3] = 32'hF0000004; // LEDR output address

    #50;

    $display("FINAL SW=%b LEDR=%b expected=%b",
        SW, LEDR, SW);

    $finish;
end

endmodule