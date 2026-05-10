`timescale 1ns/1ps

module cpu_alu_tb;

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

    // ADDI R1,R2,5
    uut.imem[16] = 32'h12000508;

    #10;
    reset = 0;

    uut.rf0.regs[2] = 10;

    #20;

    $display("FINAL R1=%0d expected=15",
        uut.rf0.regs[1]);

    $finish;
end

endmodule
