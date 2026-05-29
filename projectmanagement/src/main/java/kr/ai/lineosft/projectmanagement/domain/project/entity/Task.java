package kr.ai.lineosft.projectmanagement.domain.project.entity;

import jakarta.persistence.*;
import kr.ai.lineosft.projectmanagement.common.entity.BaseTimeEntity;
import kr.ai.lineosft.projectmanagement.domain.member.entity.Member;
import lombok.AccessLevel;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;

import java.time.LocalDate;

@Entity
@Getter
@NoArgsConstructor(access = AccessLevel.PROTECTED)
@Table(name = "tasks")
public class Task extends BaseTimeEntity {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false)
    private String title;

    @Column(length = 1000)
    private String description;

    @Enumerated(EnumType.STRING)
    @Column(nullable = false)
    private TaskStatus status;

    @Enumerated(EnumType.STRING)
    @Column(nullable = false)
    private TaskPriority priority;

    private LocalDate startDate;

    private LocalDate endDate;

    @Column(nullable = false)
    private Integer progress;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "project_id", nullable = false)
    private Project project;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "assignee_id")
    private Member assignee;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "sprint_id")
    private Sprint sprint;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "phase_id")
    private Phase phase;

    @Builder
    private Task(String title, String description, TaskStatus status, TaskPriority priority, LocalDate startDate, LocalDate endDate, Integer progress, Project project, Member assignee, Sprint sprint, Phase phase) {
        this.title = title;
        this.description = description;
        this.status = status != null ? status : TaskStatus.BACKLOG;
        this.priority = priority != null ? priority : TaskPriority.MEDIUM;
        this.startDate = startDate;
        this.endDate = endDate;
        this.progress = progress != null ? progress : 0;
        this.project = project;
        this.assignee = assignee;
        this.sprint = sprint;
        this.phase = phase;
    }

    public void update(String title, String description, TaskStatus status, TaskPriority priority, LocalDate startDate, LocalDate endDate, Integer progress, Member assignee, Sprint sprint, Phase phase) {
        this.title = title;
        this.description = description;
        if (status != null) {
            this.status = status;
        }
        if (priority != null) {
            this.priority = priority;
        }
        this.startDate = startDate;
        this.endDate = endDate;
        if (progress != null) {
            this.progress = progress;
        }
        this.assignee = assignee;
        this.sprint = sprint;
        this.phase = phase;
    }

    public void updateStatus(TaskStatus status) {
        if (status != null) {
            this.status = status;
        }
    }
}
