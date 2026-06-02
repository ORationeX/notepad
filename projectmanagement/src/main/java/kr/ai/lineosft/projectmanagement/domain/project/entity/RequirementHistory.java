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
@Table(name = "requirement_histories")
public class RequirementHistory {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "requirement_id", nullable = false)
    private Requirement requirement;

    @Column(nullable = false)
    private String title;

    @Column(columnDefinition = "TEXT")
    private String description;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "category_id")
    private RequirementCategory category;

    @Enumerated(EnumType.STRING)
    @Column(nullable = false)
    private RequirementPriority priority;

    @Enumerated(EnumType.STRING)
    @Column(nullable = false)
    private RequirementStatus status;

    @Column(nullable = false)
    private Integer progress;

    private String requestedBy;

    private String domainName;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "modifier_id")
    private Member modifier;

    @Column(nullable = false)
    private LocalDateTime modifiedAt;

    private String comment;

    @Builder
    private RequirementHistory(Requirement requirement, String title, String description, RequirementCategory category,
                               RequirementPriority priority, RequirementStatus status, Integer progress,
                               String requestedBy, String domainName, Member modifier, LocalDateTime modifiedAt, String comment) {
        this.requirement = requirement;
        this.title = title;
        this.description = description;
        this.category = category;
        this.priority = priority;
        this.status = status;
        this.progress = progress;
        this.requestedBy = requestedBy;
        this.domainName = domainName;
        this.modifier = modifier;
        this.modifiedAt = modifiedAt != null ? modifiedAt : LocalDateTime.now();
        this.comment = comment;
    }
}
