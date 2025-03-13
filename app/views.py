from app import app
from flask import render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from .models import db, Users, Seller, Project, Proposal, Review, Message
from datetime import datetime

@app.route('/')
def home():
    """Home page route"""
    return render_template('index.html')

@app.route('/dashboard')
@login_required
def dashboard():
    """Dashboard route for both clients and freelancers"""
    if current_user.role == 'customer':
        # For clients, show their posted projects and active contracts
        projects = Project.query.filter_by(client_id=current_user.id).all()
        active_projects = [p for p in projects if p.status in ['open', 'in_progress']]
        completed_projects = [p for p in projects if p.status == 'completed']
        
        # Get proposals for client's projects
        project_ids = [p.id for p in projects]
        proposals = Proposal.query.filter(Proposal.project_id.in_(project_ids)).all() if project_ids else []
        
        return render_template(
            'dashboard.html', 
            title='Client Dashboard',
            active_projects=active_projects,
            completed_projects=completed_projects,
            proposals=proposals
        )
    else:
        # For freelancers, show their proposals and active contracts
        proposals = Proposal.query.filter_by(freelancer_id=current_user.id).all()
        active_proposals = [p for p in proposals if p.status == 'accepted']
        pending_proposals = [p for p in proposals if p.status == 'pending']
        
        # Get projects where the freelancer has been awarded
        awarded_projects = Project.query.filter_by(awarded_to=current_user.id).all()
        
        return render_template(
            'dashboard.html', 
            title='Freelancer Dashboard',
            active_proposals=active_proposals,
            pending_proposals=pending_proposals,
            awarded_projects=awarded_projects
        )

@app.route('/marketplace')
@login_required
def marketplace():
    """Marketplace route to browse available projects"""
    # Get all open projects
    projects = Project.query.filter_by(status='open').all()
    
    # If user is a freelancer, get their proposals to check if they've already applied
    user_proposals = []
    if current_user.role != 'customer':
        user_proposals = Proposal.query.filter_by(freelancer_id=current_user.id).all()
        user_proposal_project_ids = [p.project_id for p in user_proposals]
    else:
        user_proposal_project_ids = []
    
    return render_template(
        'marketplace.html', 
        title='Project Marketplace',
        projects=projects,
        user_proposal_project_ids=user_proposal_project_ids
    )

@app.route('/project/new', methods=['GET', 'POST'])
@login_required
def new_project():
    """Route to create a new project"""
    if current_user.role != 'customer':
        flash('Only clients can create projects', 'error')
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        budget = request.form.get('budget')
        category = request.form.get('category')
        skills_required = request.form.get('skills')
        deadline_str = request.form.get('deadline')
        
        # Validate inputs
        if not title or not description or not budget or not category:
            flash('Please fill in all required fields', 'error')
            return redirect(url_for('new_project'))
        
        try:
            budget = float(budget)
            deadline = datetime.strptime(deadline_str, '%Y-%m-%d') if deadline_str else None
            
            # Create new project
            project = Project(
                title=title,
                description=description,
                budget=budget,
                category=category,
                client_id=current_user.id,
                deadline=deadline,
                skills_required=skills_required
            )
            
            db.session.add(project)
            db.session.commit()
            
            flash('Project created successfully!', 'success')
            return redirect(url_for('dashboard'))
            
        except ValueError:
            flash('Invalid input values', 'error')
            return redirect(url_for('new_project'))
    
    return render_template('project_form.html', title='Create New Project')

@app.route('/project/<project_id>')
@login_required
def view_project(project_id):
    """Route to view a specific project"""
    project = Project.query.get_or_404(project_id)
    
    # Check if user has already submitted a proposal
    user_proposal = None
    if current_user.role != 'customer':
        user_proposal = Proposal.query.filter_by(
            project_id=project_id, 
            freelancer_id=current_user.id
        ).first()
    
    # Get client info
    client = Users.query.get(project.client_id)
    
    # Get all proposals if user is the project owner
    proposals = []
    if current_user.id == project.client_id:
        proposals = Proposal.query.filter_by(project_id=project_id).all()
    
    return render_template(
        'project_detail.html',
        title=project.title,
        project=project,
        client=client,
        user_proposal=user_proposal,
        proposals=proposals
    )

@app.route('/project/<project_id>/proposal', methods=['GET', 'POST'])
@login_required
def submit_proposal(project_id):
    """Route to submit a proposal for a project"""
    if current_user.role == 'customer':
        flash('Only freelancers can submit proposals', 'error')
        return redirect(url_for('view_project', project_id=project_id))
    
    project = Project.query.get_or_404(project_id)
    
    # Check if project is still open
    if project.status != 'open':
        flash('This project is no longer accepting proposals', 'error')
        return redirect(url_for('view_project', project_id=project_id))
    
    # Check if user has already submitted a proposal
    existing_proposal = Proposal.query.filter_by(
        project_id=project_id, 
        freelancer_id=current_user.id
    ).first()
    
    if existing_proposal:
        flash('You have already submitted a proposal for this project', 'error')
        return redirect(url_for('view_project', project_id=project_id))
    
    if request.method == 'POST':
        bid_amount = request.form.get('bid_amount')
        cover_letter = request.form.get('cover_letter')
        completion_time = request.form.get('completion_time')
        
        # Validate inputs
        if not bid_amount or not cover_letter:
            flash('Please fill in all required fields', 'error')
            return redirect(url_for('submit_proposal', project_id=project_id))
        
        try:
            bid_amount = float(bid_amount)
            completion_time = int(completion_time) if completion_time else None
            
            # Create new proposal
            proposal = Proposal(
                bid_amount=bid_amount,
                cover_letter=cover_letter,
                project_id=project_id,
                freelancer_id=current_user.id,
                estimated_completion_time=completion_time
            )
            
            db.session.add(proposal)
            db.session.commit()
            
            flash('Proposal submitted successfully!', 'success')
            return redirect(url_for('view_project', project_id=project_id))
            
        except ValueError:
            flash('Invalid input values', 'error')
            return redirect(url_for('submit_proposal', project_id=project_id))
    
    return render_template(
        'proposal_form.html',
        title='Submit Proposal',
        project=project
    )

@app.route('/project/<project_id>/proposal/<proposal_id>/accept', methods=['POST'])
@login_required
def accept_proposal(project_id, proposal_id):
    """Route to accept a proposal"""
    project = Project.query.get_or_404(project_id)
    proposal = Proposal.query.get_or_404(proposal_id)
    
    # Verify that current user is the project owner
    if current_user.id != project.client_id:
        flash('You do not have permission to accept this proposal', 'error')
        return redirect(url_for('view_project', project_id=project_id))
    
    # Verify that the proposal belongs to the project
    if proposal.project_id != project_id:
        flash('Invalid proposal for this project', 'error')
        return redirect(url_for('view_project', project_id=project_id))
    
    # Update proposal status
    proposal.status = 'accepted'
    
    # Update project status and awarded freelancer
    project.status = 'in_progress'
    project.awarded_to = proposal.freelancer_id
    
    # Reject all other proposals
    other_proposals = Proposal.query.filter(
        Proposal.project_id == project_id,
        Proposal.id != proposal_id
    ).all()
    
    for other_proposal in other_proposals:
        other_proposal.status = 'rejected'
    
    db.session.commit()
    
    flash('Proposal accepted successfully!', 'success')
    return redirect(url_for('view_project', project_id=project_id))

@app.route('/project/<project_id>/complete', methods=['POST'])
@login_required
def complete_project(project_id):
    """Route to mark a project as complete"""
    project = Project.query.get_or_404(project_id)
    
    # Verify that current user is the project owner
    if current_user.id != project.client_id:
        flash('You do not have permission to complete this project', 'error')
        return redirect(url_for('view_project', project_id=project_id))
    
    # Update project status
    project.status = 'completed'
    db.session.commit()
    
    flash('Project marked as complete!', 'success')
    return redirect(url_for('view_project', project_id=project_id))

@app.route('/profile')
@login_required
def profile():
    """Route to view and edit user profile"""
    # Check if user has a profile
    seller_profile = None
    if current_user.role != 'customer':
        seller_profile = Seller.query.filter_by(user_id=current_user.id).first()
    
    return render_template(
        'profile.html',
        title='My Profile',
        user=current_user,
        profile=seller_profile
    )

@app.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    """Route to edit user profile"""
    # Get existing profile if it exists
    seller_profile = None
    if current_user.role != 'customer':
        seller_profile = Seller.query.filter_by(user_id=current_user.id).first()
    
    if request.method == 'POST':
        # Common fields for all users
        firstname = request.form.get('firstname')
        lastname = request.form.get('lastname')
        phonenumber = request.form.get('phonenumber')
        
        # Update user info
        if firstname and lastname:
            current_user.firstname = firstname
            current_user.lastname = lastname
            current_user.phonenumber = phonenumber
        
        # Additional fields for freelancers
        if current_user.role != 'customer':
            bio = request.form.get('bio')
            address = request.form.get('address')
            skill = request.form.get('skill')
            city = request.form.get('city')
            country = request.form.get('country')
            hourly_rate = request.form.get('hourly_rate')
            availability = request.form.get('availability')
            languages = request.form.get('languages')
            
            try:
                hourly_rate = float(hourly_rate) if hourly_rate else None
                
                if seller_profile:
                    # Update existing profile
                    seller_profile.bio = bio
                    seller_profile.address = address
                    seller_profile.skill = skill
                    seller_profile.city = city
                    seller_profile.country = country
                    seller_profile.hourly_rate = hourly_rate
                    seller_profile.availability = availability
                    seller_profile.languages = languages
                else:
                    # Create new profile
                    new_profile = Seller(
                        user_id=current_user.id,
                        bio=bio,
                        address=address,
                        skill=skill,
                        city=city,
                        country=country,
                        hourly_rate=hourly_rate,
                        availability=availability,
                        languages=languages
                    )
                    db.session.add(new_profile)
            
            except ValueError:
                flash('Invalid input for hourly rate', 'error')
                return redirect(url_for('edit_profile'))
        
        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('profile'))
    
    return render_template(
        'profile_edit.html',
        title='Edit Profile',
        user=current_user,
        profile=seller_profile
    )

@app.route('/messages')
@login_required
def messages():
    """Route to view user messages"""
    # Get all messages where user is sender or receiver
    sent_messages = Message.query.filter_by(sender_id=current_user.id).all()
    received_messages = Message.query.filter_by(receiver_id=current_user.id).all()
    
    # Get unique conversation partners
    conversation_partners = set()
    for msg in sent_messages:
        conversation_partners.add(msg.receiver_id)
    for msg in received_messages:
        conversation_partners.add(msg.sender_id)
    
    # Get user info for each conversation partner
    conversations = []
    for partner_id in conversation_partners:
        partner = Users.query.get(partner_id)
        if partner:
            # Get latest message
            latest_message = Message.query.filter(
                ((Message.sender_id == current_user.id) & (Message.receiver_id == partner_id)) |
                ((Message.sender_id == partner_id) & (Message.receiver_id == current_user.id))
            ).order_by(Message.created_at.desc()).first()
            
            conversations.append({
                'partner': partner,
                'latest_message': latest_message
            })
    
    return render_template(
        'messages.html',
        title='My Messages',
        conversations=conversations
    )

@app.route('/messages/<user_id>', methods=['GET', 'POST'])
@login_required
def conversation(user_id):
    """Route to view and send messages to a specific user"""
    partner = Users.query.get_or_404(user_id)
    
    if request.method == 'POST':
        content = request.form.get('message')
        project_id = request.form.get('project_id')
        
        if not content:
            flash('Message cannot be empty', 'error')
            return redirect(url_for('conversation', user_id=user_id))
        
        # Create new message
        message = Message(
            content=content,
            sender_id=current_user.id,
            receiver_id=user_id,
            project_id=project_id if project_id else None
        )
        
        db.session.add(message)
        db.session.commit()
        
        return redirect(url_for('conversation', user_id=user_id))
    
    # Get all messages between current user and partner
    messages = Message.query.filter(
        ((Message.sender_id == current_user.id) & (Message.receiver_id == user_id)) |
        ((Message.sender_id == user_id) & (Message.receiver_id == current_user.id))
    ).order_by(Message.created_at).all()
    
    # Mark unread messages as read
    unread_messages = Message.query.filter_by(
        sender_id=user_id,
        receiver_id=current_user.id,
        is_read=False
    ).all()
    
    for msg in unread_messages:
        msg.is_read = True
    
    db.session.commit()
    
    # Get projects where both users are involved
    shared_projects = []
    if current_user.role == 'customer':
        # Current user is client, partner is freelancer
        shared_projects = Project.query.filter_by(
            client_id=current_user.id,
            awarded_to=user_id
        ).all()
    else:
        # Current user is freelancer, partner is client
        shared_projects = Project.query.filter_by(
            client_id=user_id,
            awarded_to=current_user.id
        ).all()
    
    return render_template(
        'conversation.html',
        title=f'Conversation with {partner.get_full_name()}',
        partner=partner,
        messages=messages,
        shared_projects=shared_projects
    )

@app.route('/freelancers')
@login_required
def freelancers():
    """Route to browse available freelancers"""
    # Get all users with role 'seller'
    freelancer_users = Users.query.filter_by(role='seller').all()
    
    # Get their profiles
    freelancers_with_profiles = []
    for user in freelancer_users:
        profile = Seller.query.filter_by(user_id=user.id).first()
        if profile:
            freelancers_with_profiles.append({
                'user': user,
                'profile': profile
            })
    
    return render_template(
        'freelancers.html',
        title='Browse Freelancers',
        freelancers=freelancers_with_profiles
    )

@app.route('/freelancer/<user_id>')
@login_required
def view_freelancer(user_id):
    """Route to view a specific freelancer's profile"""
    user = Users.query.get_or_404(user_id)
    
    # Verify that user is a freelancer
    if user.role == 'customer':
        flash('This user is not a freelancer', 'error')
        return redirect(url_for('freelancers'))
    
    # Get freelancer profile
    profile = Seller.query.filter_by(user_id=user_id).first()
    
    # Get completed projects
    completed_projects = Project.query.filter_by(
        awarded_to=user_id,
        status='completed'
    ).all()
    
    # Get reviews
    reviews = Review.query.filter_by(reviewee_id=user_id).all()
    
    return render_template(
        'freelancer_profile.html',
        title=f"{user.get_full_name()}'s Profile",
        freelancer=user,
        profile=profile,
        completed_projects=completed_projects,
        reviews=reviews
    )

@app.route('/review/<project_id>/<user_id>', methods=['GET', 'POST'])
@login_required
def leave_review(project_id, user_id):
    """Route to leave a review for a user"""
    project = Project.query.get_or_404(project_id)
    user = Users.query.get_or_404(user_id)
    
    # Verify that the project is completed
    if project.status != 'completed':
        flash('You can only leave reviews for completed projects', 'error')
        return redirect(url_for('view_project', project_id=project_id))
    
    # Verify that current user is involved in the project
    if current_user.id != project.client_id and current_user.id != project.awarded_to:
        flash('You are not authorized to leave a review for this project', 'error')
        return redirect(url_for('view_project', project_id=project_id))
    
    # Verify that the user being reviewed is involved in the project
    if user.id != project.client_id and user.id != project.awarded_to:
        flash('This user is not involved in the project', 'error')
        return redirect(url_for('view_project', project_id=project_id))
    
    # Verify that the user is not reviewing themselves
    if current_user.id == user.id:
        flash('You cannot review yourself', 'error')
        return redirect(url_for('view_project', project_id=project_id))
    
    # Check if review already exists
    existing_review = Review.query.filter_by(
        project_id=project_id,
        reviewer_id=current_user.id,
        reviewee_id=user.id
    ).first()
    
    if existing_review:
        flash('You have already left a review for this user on this project', 'error')
        return redirect(url_for('view_project', project_id=project_id))
    
    if request.method == 'POST':
        rating = request.form.get('rating')
        comment = request.form.get('comment')
        
        if not rating:
            flash('Please provide a rating', 'error')
            return redirect(url_for('leave_review', project_id=project_id, user_id=user_id))
        
        try:
            rating = int(rating)
            if rating < 1 or rating > 5:
                raise ValueError('Rating must be between 1 and 5')
            
            # Create new review
            review = Review(
                rating=rating,
                comment=comment,
                project_id=project_id,
                reviewer_id=current_user.id,
                reviewee_id=user.id
            )
            
            db.session.add(review)
            db.session.commit()
            
            flash('Review submitted successfully!', 'success')
            return redirect(url_for('view_project', project_id=project_id))
            
        except ValueError as e:
            flash(str(e), 'error')
            return redirect(url_for('leave_review', project_id=project_id, user_id=user_id))
    
    return render_template(
        'review_form.html',
        title='Leave a Review',
        project=project,
        reviewee=user
    )

@app.route('/search')
@login_required
def search():
    """Route to search for projects or freelancers"""
    query = request.args.get('q', '')
    search_type = request.args.get('type', 'projects')
    
    results = []
    if search_type == 'projects':
        # Search for projects
        results = Project.query.filter(
            (Project.title.ilike(f'%{query}%')) |
            (Project.description.ilike(f'%{query}%')) |
            (Project.category.ilike(f'%{query}%')) |
            (Project.skills_required.ilike(f'%{query}%'))
        ).all()
    else:
        # Search for freelancers
        freelancer_users = Users.query.filter(
            (Users.role != 'customer') &
            ((Users.firstname.ilike(f'%{query}%')) |
             (Users.lastname.ilike(f'%{query}%')))
        ).all()
        
        # Get their profiles
        for user in freelancer_users:
            profile = Seller.query.filter_by(user_id=user.id).first()
            if profile and (
                query.lower() in profile.skill.lower() or
                query.lower() in profile.bio.lower() if profile.bio else False
            ):
                results.append({
                    'user': user,
                    'profile': profile
                })
    
    return render_template(
        'search_results.html',
        title='Search Results',
        query=query,
        search_type=search_type,
        results=results
    )
