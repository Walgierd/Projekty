.code

; void PixelateAsm(ptr data, int width, int height, int stride, int pixelSize, int startRow, int endRow)
PixelateAsm proc
    ; --- PROLOG ---
    push rbp
    mov rbp, rsp
    push rbx
    push rsi
    push rdi
    push r12
    push r13
    push r14
    push r15

    ; --- POBIERANIE ARGUMENTÓW ---
    mov r12, rcx        ; data ptr
    mov r13, rdx        ; width
    mov r14, r8         ; height
    mov r15, r9         ; stride

    ; Argumenty ze stosu:
    mov rbx, [rbp + 48] ; pixelSize
    mov r8,  [rbp + 56] ; startRow (Y)
    mov r9,  [rbp + 64] ; endRow

    ; --- PÊTLA Y ---
LoopY:
    cmp r8, r9
    jge EndProc

    xor r10, r10        ; X = 0

    ; --- PÊTLA X ---
LoopX:
    cmp r10, r13
    jge NextBlockY

    ; 1. SUMOWANIE
    xor rsi, rsi        ; Sum Blue
    xor rdi, rdi        ; Sum Green
    xor r11, r11        ; Sum Red
    xor rcx, rcx        ; Count

    xor rax, rax        ; by = 0
SumLoopY:
    cmp rax, rbx
    jge CalcAvg

    mov rdx, r8         ; Y
    add rdx, rax
    cmp rdx, r14        ; >= height?
    jge CalcAvg

    xor rdx, rdx        ; bx = 0
SumLoopX:
    cmp rdx, rbx
    jge NextSumRow

    ; Sprawdzenie szerokoœci (Width Check)
    push rdx            ; Zapisz bx
    add rdx, r10        ; X + bx
    cmp rdx, r13        ; >= width?
    pop rdx             ; Przywróæ bx
    jge NextSumRow

    ; Adres piksela
    push rax            ; Zapisz by
    push rdx            ; Zapisz bx

    mov rax, r8         ; Y
    add rax, [rsp+8]    ; Y + by
    imul rax, r15       ; * Stride

    mov rdx, r10        ; X
    add rdx, [rsp]      ; X + bx
    shl rdx, 2          ; * 4

    add rax, rdx
    add rax, r12        ; + Data

    ; Pobierz kolory
    movzx rdx, byte ptr [rax]
    add rsi, rdx
    movzx rdx, byte ptr [rax+1]
    add rdi, rdx
    movzx rdx, byte ptr [rax+2]
    add r11, rdx

    inc rcx             ; Count++

    pop rdx
    pop rax
    inc rdx
    jmp SumLoopX

NextSumRow:
    inc rax
    jmp SumLoopY

    ; 2. ŒREDNIA
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

    ; 3. ZAPISYWANIE
    xor rax, rax        ; by = 0
WriteLoopY:
    cmp rax, rbx
    jge NextBlockX

    mov rdx, r8
    add rdx, rax
    cmp rdx, r14
    jge NextBlockX

    xor rdx, rdx        ; bx = 0
WriteLoopX:
    cmp rdx, rbx
    jge NextWriteRow

    push rdx
    add rdx, r10
    cmp rdx, r13
    pop rdx
    jge NextWriteRow

    push rax
    push rdx

    mov rax, r8
    add rax, [rsp+8]
    imul rax, r15

    mov rdx, r10
    add rdx, [rsp]
    shl rdx, 2

    add rax, rdx
    add rax, r12

    mov byte ptr [rax], sil     ; Avg B
    mov byte ptr [rax+1], dil   ; Avg G
    mov byte ptr [rax+2], r11b  ; Avg R

    pop rdx
    pop rax
    inc rdx
    jmp WriteLoopX

NextWriteRow:
    inc rax
    jmp WriteLoopY

NextBlockX:
    add r10, rbx
    jmp LoopX

NextBlockY:
    add r8, rbx
    jmp LoopY

EndProc:
    pop r15
    pop r14
    pop r13
    pop r12
    pop rdi
    pop rsi
    pop rbx
    pop rbp
    ret
PixelateAsm endp
end