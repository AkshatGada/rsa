%% Simplified OFDM Simulation for BPSK
clear;

%% Parameters
nFFT   = 64;         % FFT size
nDSC   = 52;         % Number of data subcarriers (52 out of 64)
nSym   = 1e4;        % Number of OFDM symbols
EbN0dB = 0:10;        % Eb/No range in dB

% Convert Eb/No to Es/No accounting for subcarrier usage and cyclic prefix overhead.
EsN0dB = EbN0dB + 10*log10(nDSC/nFFT) + 10*log10(64/80);

simBer = zeros(size(EbN0dB));  % To store simulated BER for each SNR

%% Simulation Loop over SNR values
for ii = 1:length(EbN0dB)
    %% Transmitter
    % 1. Generate random bits and BPSK modulation (0 -> -1, 1 -> +1)
    bits = randi([0,1], nSym, nDSC);
    modSymbols = 2*bits - 1;
    
    % 2. Map modulated symbols onto subcarriers:
    %    Use indices 7:32 for the first 26 and 34:59 for the next 26.
    X = zeros(nSym, nFFT);
    X(:,7:32)   = modSymbols(:,1:26);
    X(:,34:59)  = modSymbols(:,27:52);
    
    % 3. Convert from frequency to time domain using IFFT with normalization.
    x_time = (nFFT/sqrt(nDSC)) * ifft(fftshift(X.')).';
    
    % 4. Append a cyclic prefix (last 16 samples of each symbol)
    x_cp = [x_time(:,end-15:end) x_time];
    
    % 5. Serialize the matrix into a single vector for transmission.
    tx_signal = reshape(x_cp.', 1, []);
    
    %% Channel: AWGN Noise Addition
    % Generate complex Gaussian noise (unit variance) and scale it.
    noise = (1/sqrt(2)) * (randn(size(tx_signal)) + 1j*randn(size(tx_signal)));
    rx_signal = sqrt(80/64) * tx_signal + 10^(-EsN0dB(ii)/20) * noise;
    
    %% Receiver
    % 1. Reshape the received signal back into symbols and remove the cyclic prefix.
    rx_matrix = reshape(rx_signal, 80, nSym).';
    rx_matrix = rx_matrix(:, 17:end);  % Remove CP, keep last 64 samples
    
    % 2. Transform the received symbols to frequency domain.
    Y = (sqrt(nDSC)/nFFT) * fftshift(fft(rx_matrix.')).';
    
    % 3. Extract the data subcarriers using the same indices used at the transmitter.
    rxSymbols = Y(:, [7:32, 34:59]);
    
    % 4. BPSK demodulation: decide by taking the sign of the real part.
    demod = sign(real(rxSymbols));
    
    % 5. Map back to bits: (-1 -> 0, +1 -> 1)
    bitsHat = (demod + 1) / 2;
    
    % 6. Count bit errors.
    simBer(ii) = sum(sum(bitsHat ~= bits)) / (nSym * nDSC);
end

%% BER Calculation and Plotting
% Theoretical BER for BPSK over AWGN.
theoryBer = 0.5 * erfc(sqrt(10.^(EbN0dB/10)));

figure;
semilogy(EbN0dB, theoryBer, 'bs-', 'LineWidth',2);
hold on;
semilogy(EbN0dB, simBer, 'mx-', 'LineWidth',2);
grid on;
xlabel('Eb/No (dB)');
ylabel('Bit Error Rate');
legend('Theory', 'Simulation');
title('OFDM BPSK BER Performance');
