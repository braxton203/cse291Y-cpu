module cpu(
    input clk,
    input reset,
    input [3:0] KEY,
    input [9:0] SW,
    output [9:0] LEDR
);

reg [31:0] pc;
reg [31:0] regs [0:15];
integer i;
integer j;

reg [31:0] imem [0:255];

reg [31:0] dmem [0:255];
integer k;

reg branch_taken;

wire [31:0] instr;
wire [3:0] opcode;
wire [3:0] fn;
wire [15:0] imm;
wire [3:0] rs2;
wire [3:0] rs1;
wire [3:0] rd;
wire [31:0] imm_sext;
wire [31:0] rs1_val;
wire [31:0] rs2_val;
wire [31:0] addr;
wire [7:0] dmem_index;
wire [3:0] br_rs1;
wire [3:0] br_rs2;
wire [31:0] br_rs1_val;
wire [31:0] br_rs2_val;

assign opcode = instr[3:0];
assign fn = instr[7:4];
assign imm = instr[23:8];
assign rs2 = instr[23:20];
assign rs1 = instr[27:24];
assign rd = instr[31:28];
assign imm_sext = {{16{imm[15]}}, imm};
assign rs1_val = regs[rs1];
assign rs2_val = regs[rs2];
assign addr = rs1_val + imm_sext;
assign dmem_index = addr[9:2]; //word-aligned
assign instr = imem[pc[9:2]]; //word-aligned
assign br_rs1 = instr[31:28];
assign br_rs2 = instr[27:24];
assign br_rs1_val = regs[br_rs1];
assign br_rs2_val = regs[br_rs2];

initial begin
    for (j = 0; j < 256; j = j + 1) begin
        imem[j] = 32'h00000000;
        dmem[j] = 32'h00000000;
    end

    branch_taken = 0;

    //imem[16] = 32'h12300000; //ADD
    //imem[17] = 32'h12300010; //SUB
    //imem[18] = 32'h12300040; //AND
    //imem[19] = 32'h12300050; //OR
    //imem[20] = 32'h12300060; //XOR
    //imem[21] = 32'h123000C0; //NAND
    //imem[22] = 32'h123000D0; //NOR
    //imem[23] = 32'h123000E0; //XNOR
//
    //imem[24] = 32'h12000508; //ADDI
    //imem[25] = 32'h12000518; //SUBI
    //imem[26] = 32'h12000548; //ANDI
    //imem[27] = 32'h12000558; //ORI
    //imem[28] = 32'h12000568; //XORI
    //imem[29] = 32'h120005C8; //NANDI
    //imem[30] = 32'h120005D8; //NORI
    //imem[31] = 32'h120005E8; //XNORI
    //
    //imem[32] = 32'h12300002; //F
    //imem[33] = 32'h12300012; //EQ
    //imem[34] = 32'h12300022; //LT
    //imem[35] = 32'h12300032; //LTE
    //imem[36] = 32'h12300082; //T
    //imem[37] = 32'h12300092; //NE
    //imem[38] = 32'h123000A2; //GTE
    //imem[39] = 32'h123000B2; //GT
//
    //imem[40] = 32'h1200050A; //FI
    //imem[41] = 32'h1200051A; //EQI
    //imem[42] = 32'h1200052A; //LTI
    //imem[43] = 32'h1200053A; //LTEI
    //imem[44] = 32'h1200058A; //TI
    //imem[45] = 32'h1200059A; //NEI
    //imem[46] = 32'h120005AA; //GTEI
    //imem[47] = 32'h120005BA; //GTI
//
    //imem[48] = 32'h12300005; //SW
    //imem[49] = 32'h12000004; //LW
//
    //imem[50] = 32'h101234B8; //MVHI

    imem[16] = 32'h23000126; // BEQ R2,R3,+1
    imem[17] = 32'h12000108; // ADDI R1,R2,1
    imem[18] = 32'h12000208; // ADDI R1,R2,2

    for (i = 0; i < 16; i = i + 1) begin
        regs[i] = 0;
    end

    //ALU and CMP
    regs[2] = 4;
    regs[3] = 10;

    //SW and LW
    //regs[2] = 12; //base address
    //regs[3] = 55; //val

    dmem[3] = 99;
end

always @(posedge clk) begin
    if (reset) begin
        pc <= 32'h40;
    end else begin

    branch_taken = 0;

    if (opcode == 4'h0) begin
        case (fn)
            4'h0: regs[rd] <= rs1_val + rs2_val;
            4'h1: regs[rd] <= rs1_val - rs2_val;
            4'h4: regs[rd] <= rs1_val & rs2_val;
            4'h5: regs[rd] <= rs1_val | rs2_val;
            4'h6: regs[rd] <= rs1_val ^ rs2_val;
            4'hC: regs[rd] <= ~(rs1_val & rs2_val);
            4'hD: regs[rd] <= ~(rs1_val | rs2_val);
            4'hE: regs[rd] <= ~(rs1_val ^ rs2_val);
            default: ;
        endcase
    end else if (opcode == 4'h8) begin
        case (fn)
            4'h0: regs[rd] <= rs1_val + imm_sext;
            4'h1: regs[rd] <= rs1_val - imm_sext;
            4'h4: regs[rd] <= rs1_val & imm_sext;
            4'h5: regs[rd] <= rs1_val | imm_sext;
            4'h6: regs[rd] <= rs1_val ^ imm_sext;
            4'hC: regs[rd] <= ~(rs1_val & imm_sext);
            4'hD: regs[rd] <= ~(rs1_val | imm_sext);
            4'hE: regs[rd] <= ~(rs1_val ^ imm_sext);
            4'hB: regs[rd] <= (imm << 16);
            default: ;
        endcase
    end else if (opcode == 4'h2) begin
        case (fn)
            4'h0: regs[rd] <= 32'd0;
            4'h1: regs[rd] <= (rs1_val == rs2_val) ? 32'd1 : 32'd0;
            4'h2: regs[rd] <= (rs1_val < rs2_val) ? 32'd1 : 32'd0;
            4'h3: regs[rd] <= (rs1_val <= rs2_val) ? 32'd1 : 32'd0;
            4'h8: regs[rd] <= 32'd1;
            4'h9: regs[rd] <= (rs1_val != rs2_val) ? 32'd1 : 32'd0;
            4'hA: regs[rd] <= (rs1_val >= rs2_val) ? 32'd1 : 32'd0;
            4'hB: regs[rd] <= (rs1_val > rs2_val) ? 32'd1 : 32'd0;
            default: ;
        endcase
    end else if (opcode == 4'hA) begin
        case (fn)
            4'h0: regs[rd] <= 32'd0;
            4'h1: regs[rd] <= (rs1_val == imm_sext) ? 32'd1 : 32'd0;
            4'h2: regs[rd] <= (rs1_val < imm_sext) ? 32'd1 : 32'd0;
            4'h3: regs[rd] <= (rs1_val <= imm_sext) ? 32'd1 : 32'd0;
            4'h8: regs[rd] <= 32'd1;
            4'h9: regs[rd] <= (rs1_val != imm_sext) ? 32'd1 : 32'd0;
            4'hA: regs[rd] <= (rs1_val >= imm_sext) ? 32'd1 : 32'd0;
            4'hB: regs[rd] <= (rs1_val > imm_sext) ? 32'd1 : 32'd0;
            default: ;
        endcase
    end else if (opcode == 4'h6) begin
        case (fn)
            4'h0: branch_taken = 0;
            4'h1: branch_taken = (br_rs1_val == br_rs2_val);
            4'h2: branch_taken = (br_rs1_val < br_rs2_val);
            4'h3: branch_taken = (br_rs1_val <= br_rs2_val);
            4'h8: branch_taken = 1;
            4'h9: branch_taken = (br_rs1_val != br_rs2_val);
            4'hA: branch_taken = (br_rs1_val >= br_rs2_val);
            4'hB: branch_taken = (br_rs1_val > br_rs2_val);
            
            4'hD: branch_taken = (br_rs1_val != 0); // BNEZ
            4'h5: branch_taken = (br_rs1_val == 0); // BEQZ
            4'h6: branch_taken = (br_rs1_val < 0); // BLTZ
            4'h7: branch_taken = (br_rs1_val <= 0); // BLTEZ
            4'hE: branch_taken = (br_rs1_val >= 0); // BGTEZ
            4'hF: branch_taken = (br_rs1_val > 0); // BGTZ
            default: branch_taken = 0;
        endcase
    end else if(opcode == 4'hB) begin
        case (fn)
        4'h0: begin
             branch_taken = 1; 
             regs[rd] <= pc + 4;
        end;
        default: branch_taken = 0;
        endcase
    end else if (opcode == 4'h4) begin
        regs[rd] <= dmem[dmem_index];
    end else if (opcode == 4'h5) begin
        dmem[dmem_index] <= rs2_val;
    end

        $display("PC=%h instr=%h op=%h fn=%h rd=R%0d rs1=R%0d(%0d) rs2=R%0d(%0d) imm=%h imm_sext=%0d R1=%0d",
            pc, instr, opcode, fn, rd, rs1, rs1_val, rs2, rs2_val, imm, imm_sext, regs[1]);
        
        if (opcode == 4'h6 && branch_taken) begin
            pc <= pc + 4 + (imm_sext << 2);
        end else if(opcode == 4'hB && branch_taken) begin
            pc <= addr;
        end else begin
            pc <= pc + 4;
        end

    end
end

endmodule