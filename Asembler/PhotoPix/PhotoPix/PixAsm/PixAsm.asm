.code

; -----------------------------------------------------------------------------
; Procedure: PixelateAsm_Average
; -----------------------------------------------------------------------------
PixelateAsm_Average proc
    ; Prologue
    push rbp
    mov rbp, rsp
    push rbx
    push rsi
    push rdi
    push r12
    push r13
    push r14
    push r15

    mov r12, rcx        
    movsxd r13, edx     ; Width
    movsxd r14, r8d     ; Height
    movsxd r15, r9d     ; Stride
    movsxd rbx, dword ptr [rbp + 48] ; pixelSize
    movsxd r8,  dword ptr [rbp + 56] ; startRow
    movsxd r9,  dword ptr [rbp + 64] ; endRow

LoopY:
    cmp r8, r9
    jge EndProc_Avg

    xor r10, r10        ; Current Col X

LoopX:
    cmp r10, r13
    jge NextBlockY

    xor rsi, rsi        ; SumB
    xor rdi, rdi        ; SumG
    xor r11, r11        ; SumR
    xor rcx, rcx        ; Count

    xor rax, rax        ; Block Y
SumLoopY:
    cmp rax, rbx
    jge CalcAvg

    mov rdx, r8         
    add rdx, rax
    cmp rdx, r14        
    jge CalcAvg

    xor rdx, rdx        ; Block X
SumLoopX:
    cmp rdx, rbx
    jge NextSumRow

    push rdx
    add rdx, r10        
    cmp rdx, r13        
    pop rdx
    jge NextSumRow

    push rax
    push rdx

    mov rax, r8         
    add rax, [rsp+8]    
    imul rax, r15       

    mov rdx, r10        
    add rdx, [rsp]      
    shl rdx, 2          

    add rax, r12        
    add rax, rdx        

    movzx rdx, byte ptr [rax]
    add rsi, rdx
    movzx rdx, byte ptr [rax+1]
    add rdi, rdx
    movzx rdx, byte ptr [rax+2]
    add r11, rdx

    inc rcx

    pop rdx
    pop rax
    inc rdx
    jmp SumLoopX

NextSumRow:
    inc rax
    jmp SumLoopY

CalcAvg:
    test rcx, rcx
    jz NextBlockX

    mov rax, rsi
    xor rdx, rdx
    div rcx
    mov rsi, rax        ; Avg B

    mov rax, rdi
    xor rdx, rdx
    div rcx
    mov rdi, rax        ; Avg G

    mov rax, r11
    xor rdx, rdx
    div rcx
    mov r11, rax        ; Avg R

    mov eax, esi        
    
    mov edx, edi        
    shl edx, 8          
    or  eax, edx        
    
    shl r11d, 16        
    or  eax, r11d       
    
    or eax, 0FF000000h

    ; Use simple scalar mov to EAX for writing later (avoid XMM alignment issues)
    mov r11d, eax ; Save color in R11D

    xor rax, rax        
WriteLoopY:
    cmp rax, rbx
    jge NextBlockX

    mov rdx, r8
    add rdx, rax
    cmp rdx, r14
    jge NextBlockX

    xor rdx, rdx        
    
    push rax
    mov rax, r8
    add rax, [rsp]
    imul rax, r15
    add rax, r12
    mov rdi, r10
    shl rdi, 2
    add rax, rdi        
    
    mov rdi, rax ; RDI = Row Start Address
    pop rax      ; Retrieve Y Loop Counter

    push rax     ; Save it again for Loop check
    
WriteLoopX:
    cmp rdx, rbx
    jge NextWriteRow

    mov rsi, r10
    add rsi, rdx
    cmp rsi, r13
    jge NextWriteRow

    mov [rdi], r11d
    
    add rdi, 4
    inc rdx
    jmp WriteLoopX

NextWriteRow:
    pop rax            
    inc rax
    jmp WriteLoopY

NextBlockX:
    add r10, rbx
    jmp LoopX

NextBlockY:
    add r8, rbx
    jmp LoopY

EndProc_Avg:
    pop r15
    pop r14
    pop r13
    pop r12
    pop rdi
    pop rsi
    pop rbx
    pop rbp
    ret
PixelateAsm_Average endp


; -----------------------------------------------------------------------------
; Procedure: PixelateAsm_Random
; -----------------------------------------------------------------------------
PixelateAsm_Random proc
    push rbp
    mov rbp, rsp
    push rbx
    push rsi
    push rdi
    push r12
    push r13
    push r14
    push r15

    mov r12, rcx        
    movsxd r13, edx     
    movsxd r14, r8d     
    movsxd r15, r9d     
    movsxd rbx, dword ptr [rbp + 48] 
    movsxd r8,  dword ptr [rbp + 56] 
    movsxd r9,  dword ptr [rbp + 64] 

LoopY_Rnd:
    cmp r8, r9
    jge EndProc_Rnd
    xor r10, r10        

LoopX_Rnd:
    cmp r10, r13
    jge NextBlockY_Rnd

    mov rcx, rbx
    mov rax, r8
    add rax, rcx
    cmp rax, r14
    jle BH_Ok
    mov rcx, r14
    sub rcx, r8
BH_Ok:
    mov rdx, rbx
    mov rax, r10
    add rax, rdx
    cmp rax, r13
    jle BW_Ok
    mov rdx, r13
    sub rdx, r10
BW_Ok:
    
    test rcx, rcx
    jz NextBlockX_Rnd
    test rdx, rdx
    jz NextBlockX_Rnd

    push rcx
    push rdx

    mov rsi, rdx        
    rdrand rax
    jc RX_Ok
    rdtsc               
    shl rdx, 32
    or rax, rdx
RX_Ok:
    xor rdx, rdx
    div rsi
    mov rdi, rdx        

    mov rsi, [rsp+8]    
    rdrand rax
    jc RY_Ok
    rdtsc
    shl rdx, 32
    or rax, rdx
RY_Ok:
    xor rdx, rdx
    div rsi
    mov rsi, rdx        

    mov rax, r8
    add rax, rsi
    imul rax, r15
    mov rdx, r10
    add rdx, rdi
    shl rdx, 2
    add rax, r12
    add rax, rdx
    
    mov eax, [rax]      

    movd xmm0, eax
    pshufd xmm0, xmm0, 0

    pop rdx 
    pop rcx 
    
    xor rsi, rsi 
FillY_Rnd:
    cmp rsi, rcx
    jge NextBlockX_Rnd

    mov rax, r8
    add rax, rsi
    imul rax, r15
    add rax, r12
    mov rdi, r10
    shl rdi, 2
    add rax, rdi

    xor rdi, rdi 
FillX_Rnd:
    cmp rdi, rdx
    jge NextRow_Rnd

    mov r11, rdx
    sub r11, rdi
    cmp r11, 4
    jl FillByte_Rnd

    movups [rax], xmm0
    add rax, 16
    add rdi, 4
    jmp FillX_Rnd

FillByte_Rnd:
    movd r11d, xmm0
    mov [rax], r11d      
    add rax, 4
    inc rdi
    jmp FillX_Rnd

NextRow_Rnd:
    inc rsi
    jmp FillY_Rnd

NextBlockX_Rnd:
    add r10, rbx
    jmp LoopX_Rnd

NextBlockY_Rnd:
    add r8, rbx
    jmp LoopY_Rnd

EndProc_Rnd:
    pop r15
    pop r14
    pop r13
    pop r12
    pop rdi
    pop rsi
    pop rbx
    pop rbp
    ret
PixelateAsm_Random endp


; -----------------------------------------------------------------------------
; Procedure: PixelateAsm_Median
; -----------------------------------------------------------------------------
PixelateAsm_Median proc
    push rbp
    mov rbp, rsp
    push rbx
    push rsi
    push rdi
    push r12
    push r13
    push r14
    push r15

    mov r12, rcx        
    movsxd r13, edx     
    movsxd r14, r8d     
    movsxd r15, r9d     
    movsxd rbx, dword ptr [rbp + 48] 
    movsxd r8,  dword ptr [rbp + 56] 
    movsxd r9,  dword ptr [rbp + 64] 

    mov rax, rbx
    imul rax, rbx
    shl rax, 3
    add rax, 15
    and rax, -16      

    mov rcx, rax               
    mov r11, rsp               
ProbeLoop:
    cmp rcx, 1000h
    jl ProbeDone
    sub r11, 1000h
    test [r11], eax 
    sub rcx, 1000h
    jmp ProbeLoop
ProbeDone:
    sub rsp, rax      
    mov rsi, rsp        ; RSI = BUFFER POINTER. MUST BE PRESERVED.

LoopY_Med:
    cmp r8, r9
    jge EndProc_Med
    xor r10, r10        

LoopX_Med:
    cmp r10, r13
    jge NextBlockY_Med

    xor rcx, rcx        
    
    xor rax, rax        
ColY:
    cmp rax, rbx
    jge Sort
    mov rdx, r8
    add rdx, rax
    cmp rdx, r14
    jge Sort

    xor rdx, rdx        
ColX:
    cmp rdx, rbx
    jge NextColRow

    push rdx
    add rdx, r10
    cmp rdx, r13
    pop rdx
    jge NextColRow

    push rax
    push rdx
    
    mov rax, r8
    add rax, [rsp+8]
    imul rax, r15
    mov rdx, r10
    add rdx, [rsp]
    shl rdx, 2
    add rax, r12
    add rax, rdx

    mov eax, [rax]      
    
    movzx rdx, al      
    mov rdi, rax
    shr rdi, 8
    and rdi, 0FFh       
    mov r11, rax
    shr r11, 16
    and r11, 0FFh       

    imul rdx, 114
    imul rdi, 587
    imul r11, 299
    add rdx, rdi
    add rdx, r11        

    shl rdx, 32
    or rdx, rax
    
    mov [rsi + rcx*8], rdx ; RSI used as Buffer Pointer here
    inc rcx

    pop rdx
    pop rax
    inc rdx
    jmp ColX

NextColRow:
    inc rax
    jmp ColY

Sort:
    cmp rcx, 1
    jle ApplyMed

    mov rdx, 1           
OutSort:
    cmp rdx, rcx
    jge ApplyMed
    mov rax, [rsi + rdx*8] 
    mov rdi, rdx
    dec rdi              
InSort:
    cmp rdi, 0
    jl InDone
    mov r11, [rsi + rdi*8]
    cmp r11, rax
    jbe InDone          
    mov [rsi + rdi*8 + 8], r11
    dec rdi
    jmp InSort
InDone:
    mov [rsi + rdi*8 + 8], rax
    inc rdx
    jmp OutSort

ApplyMed:
    test rcx, rcx
    jz NextBlockX_Med
    
    mov rax, rcx
    shr rax, 1
    mov rdx, [rsi + rax*8] ; Read result from buffer
    mov eax, edx
    or eax, 0FF000000h 
    
    ; Save color in R11D
    mov r11d, eax

    xor rax, rax        
FillY_Med:
    cmp rax, rbx
    jge NextBlockX_Med
    mov rdx, r8
    add rdx, rax
    cmp rdx, r14
    jge NextBlockX_Med
    
    push rax
    mov rax, r8
    add rax, [rsp]
    imul rax, r15
    add rax, r12
    mov rdi, r10
    shl rdi, 2
    add rax, rdi        
    
    ; Save Row Start Addr in RDI, then Restore LoopY
    mov rdi, rax
    pop rax
    push rax

    xor rdx, rdx        
FillX_Med:
    cmp rdx, rbx
    jge NxtFillRow

    ; --- FIX: Use RCX instead of RSI to preserve buffer pointer ---
    mov rcx, r10 
    add rcx, rdx
    cmp rcx, r13
    jge NxtFillRow
    ; --- END FIX ---

    ; Simple Scalar Write
    mov [rdi], r11d
    
    add rdi, 4
    inc rdx
    jmp FillX_Med

NxtFillRow:
    pop rax
    inc rax
    jmp FillY_Med

NextBlockX_Med:
    add r10, rbx
    jmp LoopX_Med
NextBlockY_Med:
    add r8, rbx
    jmp LoopY_Med

EndProc_Med:
    lea rsp, [rbp - 56]
    pop r15
    pop r14
    pop r13
    pop r12
    pop rdi
    pop rsi
    pop rbx
    pop rbp
    ret
PixelateAsm_Median endp

end