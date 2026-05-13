module pipeline_tb;

  reg clk = 0;
  reg reset = 1;
  reg [3:0] KEY = 4'b0000;
  reg [9:0] SW = 10'b0000000000;
  wire [9:0] LEDR;

  cpu uut (
    .clk(clk),
    .reset(reset),
    .KEY(KEY),
    .SW(SW),
    .LEDR(LEDR)
  );

  always #5 clk = ~clk;

  initial begin
    $dumpfile("cpu.vcd");
    $dumpvars(0, pipeline_tb);

    #10 reset = 0;

    #300;
    $finish;
  end

endmodule