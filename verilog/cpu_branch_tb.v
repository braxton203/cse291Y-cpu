`timescale 1ns/1ps

module cpu_branch_tb;

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
    KEY = 0;
    SW = 0;

    // BEQ R2,R3,+1
    // ADDI R1,R2,1  (should be skipped if taken)
    // ADDI R1,R2,2  (target)
    uut.imem[16] = 32'h23000116; // BEQ R2,R3,+1
    uut.imem[17] = 32'h12000108; // ADDI R1,R2,1
    uut.imem[18] = 32'h12000208; // ADDI R1,R2,2

    #10;
    reset = 0;

    // ---------- CASE 1: NOT TAKEN ----------
    uut.rf0.regs[2] = 10;
    uut.rf0.regs[3] = 4;

    #40;

    $display("NOT TAKEN: R1=%0d expected=12", uut.rf0.regs[1]);

    // ---------- CASE 2: TAKEN ----------
    // reset PC and registers
    reset = 1;
    #10;
    reset = 0;

    uut.rf0.regs[2] = 10;
    uut.rf0.regs[3] = 10;

    #40;

    $display("TAKEN: R1=%0d expected=12 (but skip happened)", uut.rf0.regs[1]);

    $finish;
end

endmodule
