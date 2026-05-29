package kr.ai.lineosft.projectmanagement.domain.project.entity;

import jakarta.persistence.*;
import kr.ai.lineosft.projectmanagement.domain.member.entity.Member;
import lombok.AccessLevel;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;

@Entity
@Getter
@NoArgsConstructor(access = AccessLevel.PROTECTED)
@Table(name = "task_histories")
public class TaskHistory {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "task_id", nullable = false)
    private Task task;

    @Enumerated(EnumType.STRING)
    private TaskStatus fromStatus;

    @Enumerated(EnumType.STRING)
    @Column(nullable = false)
    private TaskStatus toStatus;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "modifier_id")
    private Member modifier;

    @Column(nullable = false)
    private LocalDateTime modifiedAt;

    private String comment;

    @Builder
    private TaskHistory(Task task, TaskStatus fromStatus, TaskStatus toStatus, Member modifier, LocalDateTime modifiedAt, String comment) {
        this.task = task;
        this.fromStatus = fromStatus;
        this.toStatus = toStatus;
        this.modifier = modifier;
        this.modifiedAt = modifiedAt != null ? modifiedAt : LocalDateTime.now();
        this.comment = comment;
    }
}
