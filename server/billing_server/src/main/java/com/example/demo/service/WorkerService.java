package com.example.demo.service;

import com.example.demo.dto.LoginRequest;
import com.example.demo.dto.WorkerRequest;
import com.example.demo.model.Worker;
import com.example.demo.model.WorkerSession;
import com.example.demo.repository.WorkerRepository;
import com.example.demo.repository.WorkerSessionRepository;

import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;

import java.time.Duration;
import java.time.LocalDate;
import java.time.LocalDateTime;
import java.util.List;

@Service
public class WorkerService {

    private final WorkerRepository workerRepository;
    private final WorkerSessionRepository sessionRepository;
    private final PasswordEncoder passwordEncoder;

    public WorkerService(
            WorkerRepository workerRepository,
            WorkerSessionRepository sessionRepository,
            PasswordEncoder passwordEncoder) {

        this.workerRepository = workerRepository;
        this.sessionRepository = sessionRepository;
        this.passwordEncoder = passwordEncoder;
    }

    // =========================================================
    // LOGIN
    // =========================================================

    public Worker login(LoginRequest request) {

        if (request == null) {
            throw new RuntimeException("Login request is empty");
        }

        String username = request.getUsername();
        String password = request.getPassword();

        if (username == null || username.isBlank()) {
            throw new RuntimeException("Username is required");
        }

        if (password == null || password.isBlank()) {
            throw new RuntimeException("Password is required");
        }

        Worker worker = workerRepository
                .findByUsername(username.trim())
                .orElseThrow(() ->
                        new RuntimeException(
                                "Username not found: " + username
                        ));

        System.out.println("LOGIN USER FOUND: " + worker.getUsername());
        System.out.println("PASSWORD HASH: " + worker.getPassword());

        if (worker.getPassword() == null ||
                worker.getPassword().isBlank()) {

            throw new RuntimeException(
                    "Password hash is empty for this worker"
            );
        }

        boolean valid = passwordEncoder.matches(
                password,
                worker.getPassword()
        );

        System.out.println("PASSWORD MATCH: " + valid);

        if (!valid) {
            throw new RuntimeException(
                    "Invalid password"
            );
        }

        if (worker.getStatus() != null &&
                "INACTIVE".equalsIgnoreCase(worker.getStatus())) {

            throw new RuntimeException(
                    "Worker account is inactive"
            );
        }

        WorkerSession session = new WorkerSession();

        session.setWorkerId(worker.getWorkerId());
        session.setLoginTime(LocalDateTime.now());
        session.setSessionDate(LocalDate.now());

        sessionRepository.save(session);

        return safeWorker(worker);
    }

    // =========================================================
    // SIGNUP
    // =========================================================

    public Worker signup(WorkerRequest request) {

        if (request.getUsername() == null ||
                request.getUsername().isBlank()) {

            throw new RuntimeException("Username is required");
        }

        if (request.getPassword() == null ||
                request.getPassword().isBlank()) {

            throw new RuntimeException("Password is required");
        }

        if (workerRepository
                .findByUsername(request.getUsername())
                .isPresent()) {

            throw new RuntimeException("Username already exists");
        }

        Worker worker = new Worker();

        worker.setName(request.getName());
        worker.setAge(request.getAge());
        worker.setPhone(request.getPhone());
        worker.setUsername(request.getUsername());

        // Store BCrypt hash
        worker.setPassword(
                passwordEncoder.encode(request.getPassword())
        );

        if (request.getRole() == null ||
                request.getRole().isBlank()) {

            worker.setRole("USER");

        } else {

            worker.setRole(request.getRole());
        }

        if (request.getStatus() == null ||
                request.getStatus().isBlank()) {

            worker.setStatus("ACTIVE");

        } else {

            worker.setStatus(request.getStatus());
        }

        worker.setJoinedDate(LocalDate.now());

        Worker savedWorker = workerRepository.save(worker);

        return safeWorker(savedWorker);
    }

    // =========================================================
    // UPDATE
    // =========================================================

    public Worker update(Long id, WorkerRequest request) {

        Worker worker = workerRepository
                .findById(id)
                .orElseThrow(() ->
                        new RuntimeException("Worker not found"));

        // Username
        if (request.getUsername() != null &&
                !request.getUsername().isBlank() &&
                !request.getUsername()
                        .equals(worker.getUsername())) {

            workerRepository
                    .findByUsername(request.getUsername())
                    .ifPresent(existing -> {

                        if (!existing.getWorkerId().equals(id)) {

                            throw new RuntimeException(
                                    "Username already exists"
                            );
                        }
                    });

            worker.setUsername(request.getUsername());
        }

        // Name
        if (request.getName() != null) {
            worker.setName(request.getName());
        }

        // Age
        if (request.getAge() != null) {
            worker.setAge(request.getAge());
        }

        // Phone
        if (request.getPhone() != null) {
            worker.setPhone(request.getPhone());
        }

        // Role
        if (request.getRole() != null &&
                !request.getRole().isBlank()) {

            worker.setRole(request.getRole());
        }

        // Status
        if (request.getStatus() != null &&
                !request.getStatus().isBlank()) {

            worker.setStatus(request.getStatus());
        }

        // Password
        if (request.getPassword() != null &&
                !request.getPassword().isBlank()) {

            worker.setPassword(
                    passwordEncoder.encode(
                            request.getPassword()
                    )
            );
        }

        Worker updatedWorker =
                workerRepository.save(worker);

        return safeWorker(updatedWorker);
    }

    // =========================================================
    // LOGOUT
    // =========================================================

    public void logout(Long workerId) {

        sessionRepository
                .findFirstByWorkerIdAndLogoutTimeIsNullOrderByLoginTimeDesc(
                        workerId
                )
                .ifPresent(session -> {

                    LocalDateTime logoutTime =
                            LocalDateTime.now();

                    session.setLogoutTime(logoutTime);

                    long minutes =
                            Duration.between(
                                    session.getLoginTime(),
                                    logoutTime
                            ).toMinutes();

                    session.setDurationMinutes(minutes);

                    sessionRepository.save(session);
                });
    }

    // =========================================================
    // GET WORKER SESSIONS
    // =========================================================

    public List<WorkerSession> sessions(
            Long workerId,
            LocalDate from,
            LocalDate to) {

        return sessionRepository
                .findByWorkerIdAndSessionDateBetween(
                        workerId,
                        from,
                        to
                );
    }

    // =========================================================
    // REMOVE PASSWORD FROM RESPONSE
    // =========================================================

    private Worker safeWorker(Worker worker) {

        worker.setPassword(null);

        return worker;
    }
}