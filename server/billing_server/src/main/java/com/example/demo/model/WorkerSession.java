package com.example.demo.model;

import jakarta.persistence.*;
import java.time.*;

@Entity
@Table(name = "worker_sessions")
public class WorkerSession {
	@Id
	@GeneratedValue(strategy = GenerationType.IDENTITY)
	private Long sessionId;
	@Column(nullable = false)
	private Long workerId;
	@Column(nullable = false)
	private LocalDateTime loginTime;
	private LocalDateTime logoutTime;
	private Long durationMinutes;
	private LocalDate sessionDate;

	public Long getSessionId() {
		return sessionId;
	}

	public void setSessionId(Long v) {
		sessionId = v;
	}

	public Long getWorkerId() {
		return workerId;
	}

	public void setWorkerId(Long v) {
		workerId = v;
	}

	public LocalDateTime getLoginTime() {
		return loginTime;
	}

	public void setLoginTime(LocalDateTime v) {
		loginTime = v;
	}

	public LocalDateTime getLogoutTime() {
		return logoutTime;
	}

	public void setLogoutTime(LocalDateTime v) {
		logoutTime = v;
	}

	public Long getDurationMinutes() {
		return durationMinutes;
	}

	public void setDurationMinutes(Long v) {
		durationMinutes = v;
	}

	public LocalDate getSessionDate() {
		return sessionDate;
	}

	public void setSessionDate(LocalDate v) {
		sessionDate = v;
	}
}